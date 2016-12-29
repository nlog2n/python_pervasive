#!/usr/bin/python
#
# Cricket.py
#
# Written by Ken Steele <steele@lcs.mit.edu>
#
# This program works with the Cricket location reporting system
# Developed at the MIT Laboratory for Computer Science. The program
# gpsd, modified to support cricket formats is required as the
# interface between the Cricket's serial format and the socket
# listened to by this program.
#
# It shows the nearest 10 beacons heard and connects to a web site to
# report the closest beacon when that changes.
# The socket listening code and GTK framework was borrowed from
# pygps by Russell Nelson <nelson@crynwr.com>
#
# The GUI uses GTK and the Python interface pygtk. The GUI is
# defined by the file cricket.glade
#

import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import socket, string
import os
import re
import time
import sys

valid_beacon_pattern = re.compile(r'^[A-Za-z0-9-_:.]+$')

# Seconds before a beacon not heard from is dropped
beacon_age_coeff = 0		# Distance handi-cap per second of Age

# Globals
beacons_heard = {}
g_max_beacons = 10
line_remainder = ""

w = None

class Beacon:
    def __init__(self,name,distance,id=""):
	self.name = name
	self.id = id
	self.distance = float(distance)
	self.time = time.time()
        self.battery_age = -1

    def age(self):
	return time.time() - self.time

    def __str__(self):
	return "Beacon:'%s' ID=%s dist=%0.1f age=%0.1f" % (self.name, self.id, self.distance, self.age())


def display_beacon(beacon,idx):
    "Display a beacon in the GUI"
    w.get_widget('BeaconName'+str(idx)).set_text(beacon.name)
    w.get_widget('BeaconID'+str(idx)).set_text(str(beacon.id))
    w.get_widget('BeaconDist'+str(idx)).set_text("%0.1f" % (beacon.distance))
    w.get_widget('BeaconAge'+str(idx)).set_text("%0.1f" % (beacon.age()) )


def clear_beacon_display(idx):
    "Clear the beacon display slow in the GUI"
    w.get_widget('BeaconName'+str(idx)).set_text("")
    w.get_widget('BeaconID'+str(idx)).set_text("")
    w.get_widget('BeaconDist'+str(idx)).set_text("")
    w.get_widget('BeaconAge'+str(idx)).set_text("")

def beacon_cmp_distance(beacon1, beacon2):
    "Compare beacon distances"
    if beacon1.distance < beacon2.distance:
	return -1
    else:
	if beacon1.distance > beacon2.distance:
	    return 1
	else:
	    return 0

def beacon_cmp_aged_distance(beacon1, beacon2):
    "Compare beacon distances, handicapped by age"
    global beacon_age_coeff
    d1 = beacon1.distance + beacon1.age()*beacon_age_coeff
    d2 = beacon1.distance + beacon2.age()*beacon_age_coeff
    if d1 < d2:
	return -1
    else:
	if d1 > d2:
	    return 1
	else:
	    return 0

def remove_old_beacons(beacons_dict, age_limit):
    "Remove beacons older than a certain age"
    for beacon_key in beacons_dict.keys():
	if beacons_dict[beacon_key].age() > age_limit:
	    del beacons_dict[beacon_key]

def convert_raw_distance(raw_distance):
    """
    Convert the raw distance (in Bodhi's) reported by the Cricket listener to centimeters
    Assumes the speed of sound is 344.49 m/s
    """

    # Assumed speed of sound 344.49 m/s 
    # Returns cm's
    return (float(raw_distance) - 36) * 2.2


def order_beacons(beacons_dict):
    "Sort beacons by distance"
    beacon_list = beacons_dict.values()
    beacon_list.sort(beacon_cmp_distance)
    return beacon_list


def handle_line(line):
    global beacons_heard, valid_beacon_pattern
    print "'"+line+"'"

    beacon = Beacon("",0)
    if line[0] == 'V':
        words = string.split(line, ',')
	if words[0] == 'VR':
	    beacon_name = string.strip(words[2])
            beacon_dist = words[1]
	    beacon = Beacon(beacon_name,beacon_dist)
	elif words[0] == 'VR=2.0':
	    values_dict = {}
	    for key_value in words[1:]:
                key_value_pair = string.split(key_value,"=")
		key = key_value_pair[0]
		if len(key) < 20:
   	           values_dict[key_value_pair[0]] = key_value_pair[1]
            # Check that distance, space and id are all specified
	    if not values_dict.has_key("SP"): 
                print "Missing space:",line
	        return
	    if not values_dict.has_key("DB"): 
                print "Missing dist:",line
	        return
	    if not values_dict.has_key("ID"): 
                print "Missing ID",line
	        return
            # Distance and ID is in Hex. ID offset by 32
	    beacon = Beacon(values_dict["SP"], values_dict["DB"], values_dict["ID"])
        else:
            print "Unknown sentence:",line
	    return

        if not re.match(valid_beacon_pattern, beacon.name):
	# Must be a letter, number or "-_:"
            print "Invalid ",beacon,"Len=",len(beacon.name)

        else:             
  	    beacons_heard[beacon.name] = beacon
    else:
        print "Junk:",line

def handle_input(sock, condition):
    global line_remainder
    line = s.recv(1024)
    if not line: return			# arguably we should do more.
    lines = line_remainder + line
    lines = string.split(lines, '\n')
    for line in lines[:-1]:
        handle_line(line)
    line_remainder = lines[-1]

    update_beacons()
    return 1

def beacon_time_out():
    "Maximum age of a beacon in Seconds before it is removed from the list"
    return w.get_widget('BeaconTimeOutSpin').get_value_as_int()

def historisis_time():
    "Lock out time for previous beacon in Seconds"
    return w.get_widget('PreviousLockOutSpin').get_value_as_int()


def update_beacons():
    global beacons_heard
    global reported_location, previous_location, last_reported_location

    remove_old_beacons(beacons_heard,beacon_time_out())
    ordered_beacons = order_beacons(beacons_heard)
    update_beacon_display(ordered_beacons)    

    #
    # Report location to web server
    #
    # Pick the closest
    #
    # Handicap each beacon's distance by adding a muliple of it's age
    #
    aged_ordered_beacons = ordered_beacons
    aged_ordered_beacons.sort(beacon_cmp_aged_distance)
    if aged_ordered_beacons:
        new_location = aged_ordered_beacons[0]
        if new_location.name != last_reported_location.name :
            # Don't immediately go back to the previous location
	    # TODO - Should this be a set of previous locations?
            if new_location.name == previous_location.name and previous_location.age() < historisis_time():
	        return
            set_current_location(new_location)


def set_current_location(new_location):
    "Remember the value of the current location and display it in GUI"
    global reported_location, previous_location
    
    previous_location = reported_location
    reported_location = new_location

    if previous_location.name != new_location.name: 
       w.get_widget('CricketBeacon').set_text(new_location.name)


def update_beacon_display(ordered_beacons):
    global g_max_beacons
    rank = 1
    for beacon in ordered_beacons:
        display_beacon(beacon,rank)
	rank = rank + 1
	if rank > g_max_beacons:
	   return

    # Clear remaining slots
    while rank <= g_max_beacons:
	clear_beacon_display(rank)
	rank = rank + 1

def manually_report_location(*args):
    "Manually send current location to the web site for current user"
    global reported_location, previous_location
    
    location_name = w.get_widget('SetLocationCombo').entry.get_text()
    new_location = Beacon(location_name,0)

    set_current_location(new_location)
    report_location_to_server(new_location)


def execute_query(*args):
    "Query web site for location of selected person"

    w.get_widget('QueryResult').set_text("No queries")

def idle():
    update_beacons()
    return 1

if len(sys.argv) > 1:
    cricketd_host = sys.argv[1]
else:
    cricketd_host = "127.0.0.1"

if len(sys.argv) > 2:
    cricketd_port = sys.argv[2]
else:
    cricketd_port = 2947
    
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((cricketd_host, cricketd_port))

# Ask Cricketd to start sending data on this socket
s.send("r\n")

lines = ""

glade_file = 'cricket.glade'
if not os.path.exists(glade_file):
    glade_file = '/usr/share/pycricket/cricket.glade'




w = gtk.glade.XML (glade_file,
                   "cricketApp")
dic = {"on_close_clicked": gtk.mainquit,
       "on_SetLocationButton_clicked": manually_report_location,
       "on_QueryUpdate_clicked": execute_query,
       "on_cricketApp_destroy": gtk.mainquit}

w.signal_autoconnect (dic)


##
## Query web site for know people
##
known_people_list = ["Ken Steele", "Jim Glass"]


# Add list of possible names for Identity ComboBox
IdentCombo = w.get_widget('IdentityCombo')
IdentCombo.set_popdown_strings(known_people_list)

# Add list of possible names for Query box
w.get_widget('QueryNameCombo').set_popdown_strings(known_people_list)

# Short list of known locations
known_locations_list = ["613A", "503B"]
w.get_widget('SetLocationCombo').set_popdown_strings(known_locations_list)

# Dictionary keyed by beacon name and holding a distance
beacons_heard = { }

# Reported Location beacon name
reported_location = Beacon("",0)
previous_location = Beacon("",0)
last_reported_location = Beacon("",0)


gtk.input_add(s, gtk.gdk.INPUT_READ, handle_input)
gtk.idle_add(idle)

gtk.mainloop ()
