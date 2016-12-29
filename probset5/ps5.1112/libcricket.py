#
# Cricket Interface module cricket-interface.py
#
# Written by Ken Steele <steele@lcs.mit.edu>
#
#
# This program works with the Cricket location reporting system
# developed at the MIT Laboratory for Computer Science. The program
# cricketd, a modified version of gpsd, to support cricket formats is
# required as the interface between the Cricket's serial format and
# the socket listened to by this program.
#


import socket, string
import os
import re
import time




# Globals
g_max_beacons = 4
g_cricket_handler = None
g_breacon_time_out = 15  # Age, in seconds, for removal from heard
			 # beacons list
g_mode_bin_size = 2
g_minimum_ultrasound_duration = 6  # Bodhi units

def beacon_time_out():
    global g_breacon_time_out
    return g_breacon_time_out

def mode_bin_size():
    global g_mode_bin_size
    return g_mode_bin_size


########################################

## Stores all the information for a single beacon.  A sliding time
## window of BeaconReadings (instances of the beacon being heard) is
## kept, from which a filtered distance to the beacons is created.
##
## This class is used by CricketLocationHandler

class Beacon:

    def __init__(self,name="",dist=0):
        self.name = name
        self.distance = dist
        self.time = time.time()
        self.readings = []   # Empty list
        self.count = 0

    def age(self):
        return time.time() - self.time

    def age_str(self):
        "Printable age string"
        return "%0.1f" % (self.age())

    def __str__(self):
        return "Beacon:'%s' dist=%3d age=%0.1f" % (self.name,
self.distance, self.age())

    def new_reading(self,reading):
        "New distance measurement for this beacon"

        # Remove old readings from the front of the list
        self.readings = remove_old_readings(self.readings,beacon_time_out())

        # Add the new reading at the end of the list
        self.readings.append(reading)

        # Calculate new distance
        self.calculate_distance_mode()

        # Update beacon's age to be age of youngest reading
        self.time = time.time()

    def calculate_distance_mean(self):
        """
        Calculate beacon distance given a set of readings
        Using a simple mean.
        """

        distance = 0
        self.count = len(self.readings)
        for reading in self.readings:
            distance = distance + reading.distance
        self.distance = int(distance / self.count)

    def calculate_distance_mode(self):
        """
        Calculate beacon distance given a set of readings
        Using the mode of binned values.
        """

        bin_size = mode_bin_size()
        # Sort readings into bins
        bins = {}
        max = 0
        for reading in self.readings:
            bin = int(reading.distance / bin_size)
            count,dist = bins.get(bin,(0,0))
            count = count + 1
            dist = dist + reading.distance
            bins[bin] = (count,dist)
            if count > max:
                max = count

        # Walk over all bins taking the average of the bins with
        # the Max count
        distance = 0
        max_bin_count=0
        max_bin_list = []  # diagnostist
        for bin in bins.keys():
            count,dist = bins[bin]
            if count == max:
                # Add the average of the bin's readings
                bin_value = (dist / count)
                distance = distance + bin_value
                max_bin_count = max_bin_count + 1
                max_bin_list.append(bin_value)    # diagnostist

        self.distance = distance / max_bin_count
        self.max = max
        self.count = len(self.readings)

        # diagnostics
        ##if max_bin_count > 1:
        ##   print "Max=",max," for",self.name
        ##   print "   ",max_bin_count,":",max_bin_list


###########################################################################

## This class (structure) stores the data from one ultrasound
## reception; a beacon name, distance and the time it was heard.
##
## Note: Duration (of the received ultrasound pulse) is now obselete.

class BeaconReading:

    # One distance reading from a beacon

    
    def __init__(self,name,distance,duration=0):
        self.name = name
        self.distance = distance
        self.duration = duration
        self.time = time.time()

    def age(self):
        return time.time() - self.time

    def age_str(self):
        "Printable age string"
        return "%0.1f" % (self.age())

    def __str__(self):
        #return "Beacon:'%s' dist=%3dmm age=%0.1fs" % (self.name,
        # self.distance, self.age())
        return "Beacon:'%s' dist=%3dmm duration=%0.1fms" % (self.name,
		self.distance, self.duration*(64/1000.0))


##########################################################################



def beacon_cmp_distance(beacon1, beacon2):
    "Compare beacon distances"
    if beacon1.distance < beacon2.distance:
        return -1
    else:
        if beacon1.distance > beacon2.distance:
            return 1
        else:
            return 0

def beacon_cmp_names(beacon1, beacon2):
    "Compare beacon distances"
    if beacon1.name < beacon2.name:
        return -1
    else:
        if beacon1.name > beacon2.name:
            return 1
        else:
            return 0


def remove_old_readings(reading_list, age_limit):
    """
    Remove beacons older than a certain age.
    The list is sorted oldest to newest, so find the
    first reading that meets the age limit
    """
    idx=0
    for reading in reading_list:
        if reading.age() <= age_limit:
            return reading_list[idx:]
        idx=idx+1
    return []  # Empty list
            


def convert_raw_distance(raw_distance):
    """
    Convert the raw distance (in Bodhi's = 1 15.625 KHz cycle = 64us )
reported by the Cricket listener to millimeters
    Assumes the speed of sound is 344.49 m/s
    """

    # Assumed speed of sound 344.49 m/s
    # Returns mm's
    distance = (raw_distance - 36) * 22
    return distance


def order_beacons(beacons_dict,order_function=beacon_cmp_distance):
    "Sort beacons by distance"
    beacon_list = beacons_dict.values()
    beacon_list.sort(order_function)
    return beacon_list


def filter_beacons(beacon_list,count_min):
    """
    Filter beacons that should not be included in the closest beacon
    calculation.  Must have at least two values in the same mode bin
    """
    
    result = []
    for beacon in beacon_list:
        if beacon.max >= count_min:
            result.append(beacon)
    return result




###########################################################################

## Class to handle input from a Cricket Listener.  Parses the raw data
## that we see when we telnet to port 2947 while running cricketd.
## (e.g., $Cricket2,ver=3.0,id=0,space=MIT4,distance=3B,duration=10
##
## Only one instance of this class is needed per Cricket Listener
##
## Use register_callback() to register a function that will be called
## for each ultrasound reception.  A BeaconReading object is passed
## to the function.  Multiple callback functions can be registered.
##

class CricketHandler:

    def __init__(self,host="127.0.0.1",port=2947):
        self.line_remainder = ""
        self.valid_beacon_pattern = re.compile(r'^[A-Za-z0-9-_:.]+$')
        self.callback_functions = []

        # Open socket to get data from Cricket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host,port))

        self.socket.send("r\n")

        self.minimum_ultrasound_duration = 0


    def register_callback(self,callback_func):
        self.callback_functions.append(callback_func)

    def mysocket(self):
        return self.socket

# gets called by handle_input() to parse each line of raw Cricket data.

    def handle_line(self, line):
        global g_minimum_ultrasound_duration

        reading = BeaconReading("",0)
        if line[0] == '$':
            words = string.split(line, ',')
            if words[0] == '$CRICKET':
                # $CRICKET,<dist>,<beacon-name>
                beacon_name = string.strip(words[2])
                beacon_dist = words[1]
                reading = BeaconReading(beacon_name,beacon_dist)
            elif words[0] == '$Cricket2':
                 # $CRICKET2,space=503B,id=20,dist=1C
                values_dict = {}
                for key_value in words[1:]:
                    key_value_pair = string.split(key_value,"=")
                    values_dict[key_value_pair[0]] = key_value_pair[1]
                # Check that distance, space and id are all specified
                if not values_dict.has_key("space"):
                    print "Missing space:",line
                    return
                if not values_dict.has_key("dist"):
                    print "Missing dist:",line
                    return
                if not values_dict.has_key("id"):
                    print "Missing ID",line
                    return

                # Length of detected ultrasound pulse
                duration = eval('0x'+values_dict.get("duration","0"))

                # Distance and ID are in Hex. ID offset by 32
                reading = BeaconReading(values_dict["space"],
                              
		convert_raw_distance(eval('0x'+values_dict["dist"])),
                                duration)

                # Throw away reading with small Ultra sound pulse durations as
                # they are likely to be noisy.
                if duration < g_minimum_ultrasound_duration:
                    print "Duration (",duration,") to small for",reading
                    return

            else:
                print "Unknown sentence:",line
                return

            if not re.match(self.valid_beacon_pattern, reading.name):
                # Must be a letter, number or "-_:"
                print "Invalid ",reading
                return

            if reading.distance < 0:
                # Ignore negative readings
                ##print "Negative Beacon distance",reading
                return

            # Valid Beacon reading
            # Call each registered callback function
            for callback_func in self.callback_functions:
                callback_func(reading)

        else:
            print "Junk:",line

    def handle_input(self):

        line = self.socket.recv(1024)
        if not line: return                     # arguably we should
                                                # do more.
        lines = self.line_remainder + line
        lines = string.split(lines, '\n')
        for line in lines[:-1]:
            self.handle_line(line)
        self.line_remainder = lines[-1]




###########################################################################

##
## Keeps track of the closest beacon.
##
## This class registers a callback with a CricketHandler to get called
## for every ultrasound reception.  It keeps a list of Beacons, which
## keep a list of recent transmissions from the beacon.  The list of
## beacons is sorted by their filtered distances.
##
## Allows anyone to register a callback function that is called when
## a new beacon becomes the closest beacon.  
##

class CricketLocationHandler:

    def __init__(self,cricket_handler=None):

        if cricket_handler:
            self.cricket_handler = cricket_handler
        else:
            self.cricket_handler = CricketHandler()

        # Dictionary keyed by beacon name and holding a distance
        self.beacons_heard = {}

        # Reported Location beacon name
        self.current_location = Beacon()
        self.previous_location = Beacon()

        #
        # register a callback with the cricket handler
        # Called with a beacon reading when a new one is heard
        #
        self.cricket_handler.register_callback(self.new_beacon_reading)

        self.callback_functions = []

        # Default values for settings

        self.min_beacon_readings = 2    # Minimum number of readings per
                                        # beacon to be a new location


    def register_callback(self,callback_func):
        """ Function to call when location changes
            Function is called back with location name
        """
        self.callback_functions.append(callback_func)


    def new_beacon_reading(self,reading):
        """New valid beacon reading. Add it to the set of known beacons
           and update the statistics
        """
    
        if self.beacons_heard.has_key(reading.name):
            # This beacon has been heard recently
            self.beacons_heard[reading.name].new_reading(reading)
        else:
            # New beacon
            new_beacon = Beacon(reading.name)
            new_beacon.new_reading(reading)
            self.beacons_heard[reading.name] = new_beacon

        self.update_beacons()


    def update_beacons(self):
    
        self.remove_old_beacons(beacon_time_out())
    
        #
        # Pick the closest beacon as the current location if beacon
        # times out
        #
        distance_ordered_beacons = order_beacons(self.beacons_heard,beacon_cmp_distance)
        distance_ordered_beacons = filter_beacons(distance_ordered_beacons,self.min_beacon_readings)
        if distance_ordered_beacons:
            new_location = distance_ordered_beacons[0]
            if new_location.name != self.current_location.name :
                self.set_current_location(new_location)


    def remove_old_beacons(self, age_limit):
        "Remove beacons older than a certain age"
        for beacon_key in self.beacons_heard.keys():
            if self.beacons_heard[beacon_key].age() > age_limit:
                del self.beacons_heard[beacon_key]


    def set_current_location(self,new_location):
        """Remember the value of the current location and callback to
		users who want the information"""
        
        self.previous_location = self.current_location
        # Create a copy of the beacon to make the age valid for the
        #location
        self.current_location = Beacon(new_location.name)

        # Callback registered functions
        for callback_func in self.callback_functions:  
            callback_func(new_location.name,new_location.distance)


###########################################################################




if __name__ == '__main__':
    # Test this module by printing new locations

    import sys
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = "127.0.0.1"

    def print_location(name,distance):
        print "New Location='"+name+"'","Distance =",distance,"mm"

    def print_beacon_reading(reading):
        print reading

    cricket_handler = CricketHandler(host)
    location_handler = CricketLocationHandler(cricket_handler)

    # Register handler to report when new location is found
    # Beacon() is processing data so that only new locations are
    # reported
    # location_handler.register_callback(print_location)

    # Register handler to report each Beacon heard
    # BeaconHandler() reports values from every pulse of ultrasound
    cricket_handler.register_callback(print_beacon_reading)

    while(1):
        cricket_handler.handle_input()



