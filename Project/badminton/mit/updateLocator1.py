#!/usr/bin/python

from socket import *
import cricketLocator
import random
import time
from configure import *

print "Starting Update Locator CR1..."
#Host and Port of Master Locator
if "MIT" == network_side:
    port = port_masterlocator0
else:
    port = port_masterlocator1
    
addr = (localhost,port)

sock=socket(AF_INET,SOCK_DGRAM)
# Change this to be variable later like as follows:
#name=raw_input("Please enter location name in format (RC#)")
name = "CR1"

#Name of beacon
beaconName='player'

c=cricketLocator.cricketLocator()
c.initListenCricket(name)

# Congestion control - time to wait before sucessive sends
while 1:
	#Basic loop - 
	#Query cricket beacon and get Distance
	#Send info to mastre server
	#Wait for a random ammount of time
	dist=c.getData(beaconName)
	msg='<'+name+'>'+'D='+str(dist)
	print "Sending -", msg
	sock.sendto(msg, addr)
	rndtime=random.randint(0,100)
	#time.sleep(rndtime/1000.)
