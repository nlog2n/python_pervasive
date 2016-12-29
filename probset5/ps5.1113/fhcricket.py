#
# Cricket handler  2004.11
# Created by Fang Hui , fh2008@hotmail.com

import socket
import string
import os
import time
import math
import sys

#####################################################################
class Beacon:

    def __init__(self,name="",dist=0,id=""):
        self.name = name
        self.x = 0
        self.y = 0
        self.distance = dist
        self.id = id
        self.time = time.time()
        self.readings = []   # Empty list
        self.beacon_time_out = 15  # Age, in seconds, for removal from heard
        self.max_reading  = 10     # at most reading buffer

    def set_xy(self, x,y):
        self.x = x
        self.y = y
        
    def age(self):
        return time.time() - self.time

    def new_reading(self, reading):
        self.readings.append(reading)
        # Update beacon's age to be age of youngest reading
        self.time = time.time()

        if len(self.readings) > self.max_reading :
            self.readings = self.readings[1:]
        
    def remove_old_readings(self):
    #   Remove beacons older than a certain age.
    #   The list is sorted oldest to newest, so find the  first reading that meets the age limit

#       idx=0
#       for reading in self.readings :
#        if reading.age() <= age_limit:
#            return reading_list[idx:]
#        idx=idx+1

       if len(self.readings) >= self.max_reading :
          return self.readings[1:]
       return []  # Empty list

    def  get_newest_distance(self):
       if len(self.readings) >= 1 : return self.readings[-1]
       else : return None

    def get_mean_distance(self):
        distance = 0
        count = len(self.readings)
        for reading in self.readings:
            distance = distance + reading
        self.distance = int(distance / count)
        return self.distance

           
        

###########################################################################
class CricketHandler:

#    def __init__(self,host="127.0.0.1",port=2947):
#    def __init__(self,host="172.18.182.217",port=2947):
    def __init__(self,host="172.18.182.159",port=2947): # mine    
        self.line_remainder = ""
        self.callback_functions = []

        # Open socket to get data from Cricket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host,port))

        self.socket.send("r\n")

        # Dictionary keyed by beacon name and holding a distance
        self.beacons_heard = {}

        self.old_x = 0
        self.old_y = 0
        self.new_x = 0
        self.new_x = 0



    def register_callback(self,callback_func):
        self.callback_functions.append(callback_func)
        

    def convert_raw_distance(self,raw_distance):
  #  Convert the raw distance (in Bodhi's = 1 15.625 KHz cycle = 64us )reported by the Cricket listener to millimeters
  #    Assumes the speed of sound is 344.49 m/s

    # Returns mm's
      distance = (raw_distance - 36) * 22
      return distance

      # Returns cm's   return (float(raw_distance) - 36) * 2.2




    def handle_line(self,line):
    # called by handle_input() to parse each line of raw Cricket data.
    
        #print line
        beacon = Beacon("",0)
        words = string.split(line, ',')
        if words[0] != '$Cricket2': return
        
        # $CRICKET2,space=503B,id=20,dist=1C            
        values_dict = {}
        for key_value in words[1:]:
                     key_value_pair = string.split(key_value,"=")
                     key = key_value_pair[0]
                     if len(key) < 20 and len(key_value_pair)>=2:
                          values_dict[key_value_pair[0]] = key_value_pair[1]

        # Check that distance, space and id are all specified
        if not values_dict.has_key("space"):   
                   print "Missing space:"
                   return
        if not values_dict.has_key("dist"): 
                   print "Missing dist:"
                   return
        if not values_dict.has_key("id"): 
                   print "Missing ID"
                   return

        # Distance and ID is in Hex. ID offset by 32
        (space,distance) = (values_dict["space"], self.convert_raw_distance(eval('0x'+values_dict["dist"])) )
#        print space,distance
        if distance >=0 :   self.new_beacon_reading(space,distance)
             

    def handle_input(self,s,condition):

        line = self.socket.recv(1024)
        if not line: return                     
        lines = self.line_remainder + line
        lines = string.split(lines, '\n')
        for line in lines[:-1]:
            self.handle_line(line)
        self.line_remainder = lines[-1]
        
        self.update_beacons()
        
        return 1



    def new_beacon_reading(self,name, distance):
        if self.beacons_heard.has_key(name):   # This beacon has been heard recently
            self.beacons_heard[name].new_reading(distance)
        else:     # New beacon
            new_beacon = Beacon(name, distance)
            new_beacon.new_reading(distance)
            self.beacons_heard[name] = new_beacon


    def beacon_cmp_distance(self,beacon1, beacon2):
      if beacon1.distance < beacon2.distance:  return -1
      else:
        if beacon1.distance > beacon2.distance:  return 1
        else:     return 0

    def order_beacons(self):
      beacon_list = self.beacons_heard.values()
      beacon_list.sort(self.beacon_cmp_distance)
      return beacon_list


    def remove_old_beacons(self):
        #Remove beacons older than a certain age
        for beacon_key in self.beacons_heard.keys():
            if self.beacons_heard[beacon_key].age() > self.beacons_heard[beacon_key].beacon_time_out:
                del self.beacons_heard[beacon_key]


    def triangulate(self,b1,b2) :
    
          proportional  = 2
          d1 = b1.get_mean_distance()
          d2 = b2.get_mean_distance()
          if  d1 is None or d2 is None : return None


          b1.set_xy(0,0)
          b2.set_xy(2178,0)
          
          w =  b2.x
          ret_x =  ( (w*w + d1*d1 - d2*d2)/(2*w) ) / proportional
          tmp = d1*d1 - ret_x * ret_x 
          if tmp>=0 :
             ret_y =  math.sqrt(tmp) / proportional
          else :
             ret_y = 0

          return [ int(ret_x), int(ret_y)]
          
       
    def update_beacons(self):
    
        #self.remove_old_beacons()
    
        # Pick the closest beacon as the current location if beacon times out
        distance_ordered_beacons = self.order_beacons()
        if  distance_ordered_beacons is None : return 

        if len(distance_ordered_beacons) >=2 :
            b1 = distance_ordered_beacons[0]
            b2 = distance_ordered_beacons[1]
            new_location = self.triangulate(b1,b2)
            if new_location is None : return

            (new_x,new_y) = (new_location[0], new_location[1])
            if  math.fabs(self.old_x -new_x) + math.fabs(self.old_y - new_y) < 40 :  return 

            print "Point",new_location

            self.old_x = new_x
            self.old_y = new_y
            for callback_func in self.callback_functions:  
                callback_func(new_location[0],new_location[1])

    def  idle(self) :
        # self.update_beacons()
        return 1                
