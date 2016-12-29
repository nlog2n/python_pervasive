#! /usr/bin/python

from socket import *
import random
import time
import string
import math
from configure import *

class QueryLocator:


    if "MIT" == network_side:
        portML = port_masterlocator0
        portME = port_querylocator0
    else:
        portML = port_masterlocator1
        portME = port_querylocator1
        
    addrME = (localhost,portME)
    addrML = (localhost,portML)

    sock = socket(AF_INET,SOCK_DGRAM)
    sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    sock.bind(addrME)

    # Modified by Chen Binbin to use TCP socket instead of UDP to connect to Game Engine
    sock_ge = socket(AF_INET,SOCK_STREAM)
    sock_ge.connect(addrGE)
    sock_ge.send("connected by location daemon from site " + network_side)
    
    

##    # Create server sockets and bind to address for Game Engine and Master Locator
##    ServSockGE = socket(AF_INET,SOCK_DGRAM)
##    ServSockGE.bind(addrGE)
##
##    ServSockML = socket(AF_INET,SOCK_DGRAM)
##    ServSockML.bind(addrML)    
 #put in buffer area (-20 on X and -20 on Y) on location to space it properly

    # Modified by Chen Binbin to make the 9 points exactly on the border

    """
    border = 10
    PlayAreaX = 670 - 2*border
    PlayAreaY = 520 - 2*border
    Xmid = 520/2
    Xrt = Xmid + PlayAreaX/4
    Xlt = Xmid - PlayAreaX/4
    Ymid = 670/2
    Ybot = Ymid + PlayAreaY/4
    Ytop = Ymid - PlayAreaY/4"""

    Xmid = 520/2
    Xrt = 520
    Xlt = 0
    Ymid = 670/2
    Ybot = 670
    Ytop = 0
    
    SpotLocLookup = {
        1 : [Xlt, Ytop],
        2 : [Xmid, Ytop],
        3 : [Xrt, Ytop],
        4 : [Xlt, Ymid],
        5 : [Xmid, Ymid],
        6 : [Xrt, Ymid],
        7 : [Xlt, Ybot],
        8 : [Xmid, Ybot],
        9 : [Xrt, Ybot]}
    
    #sock.close()
    def __init__(self):
        self.GO = 1
       
        self.myName = "QueryGuy"
        
        #self.msg="This is " + self.myName + " getting started up"
        #self.sock.sendto(self.msg,self.addrME)
        #self.sock.sendto(self.msg,self.addrML)
        #self.sock.sendto(self.msg,self.addrGE)
        self.run()

    def run(self):
        while(self.GO):
            # wait for a request from Game Engine Server

            data,addr = self.sock_ge.recvfrom(1024)
            if (data):
                TimeAndSpot = self.get_WaitTime_and_Spot(data)
                print "queryLocator at side " + network_side + " print: the time and spot",TimeAndSpot
                self.send_HIT_or_MISS_to_GE(TimeAndSpot)

            """   
                #if request in get the location, do the logic, then send\
                if(data[1:data.find('>')] == "GameEngine"):
                    self.addrGE = addr
                    TimeAndSpot = self.get_WaitTime_and_Spot(data)
                    print "the time and spot",TimeAndSpot
                    self.send_HIT_or_MISS_to_GE(TimeAndSpot)
                elif(data[1:data.find('>')] == "MasterLocator"):
                    self.addrML = addr
            """

    def get_WaitTime_and_Spot(self, data):
        #parse data string to get time and spot this format: "<GameEngine>T=5000S=4
        time = data[data.find("T=")+2:data.find("S=")]
        spot = int(data[data.find("S=")+2:])
        return [time, spot]
    
    def get_loc_of_player(self):
        #get location of the player right now from Master Locator
        msg = "?PlayerLocation"
        self.sock.sendto(msg,self.addrML)
        print "queryLocator at side " + network_side + " print: send query to MasterLocator at port " + str(self.addrML)
        

        self.sock.settimeout(0.1)            
        data=''
        while (data ==''):
            try:
                data,addr = self.sock.recvfrom(1024)
                print "queryLocator got: " + data
                if(data[1:data.find('>')] == "GameEngine"):
                    self.addrGE = addr
                    data = ''
                elif(data[1:data.find('>')] == "MasterLocator"):
                    break
                elif(data[1:data.find('>')] != "MasterLocator"):
                    data = ''

                    
            except:
                #send new request and wait for reception
                data=''
                self.sock.sendto(msg,self.addrML)
       
        print "queryLocator at side " + network_side + " print: got this for data from MasterLocator"+str(data)
        data = string.replace(data, '\n', '')
        data = string.replace(data, "<MasterLocator>", '#')
        self.sock.settimeout(None)
        return [int(data[1:data.find(",")]),int(data[data.find(",")+1:])]
        

    def send_HIT_or_MISS_to_GE(self, tns):
        #calculate the logic of a hit or miz
        waittime = tns[0]
        spot = tns[1]
        #sleep for the specified time

        # Here may change the logic. Noted by Chen Binbin

        
        time.sleep(float(waittime))
        #awake and get dist of player and loc of spot
        pLoc = self.get_loc_of_player()
        spotLoc = self.SpotLocLookup.get(spot)
        xDiff = spotLoc[0]-pLoc[0]
        yDiff = spotLoc[1]-pLoc[1]
        distDiff = math.sqrt(xDiff*xDiff+yDiff*yDiff) 
        if(distDiff>20):
            decision = "<GameArbiter>D=MISS"
        else:
            decision = "<GameArbiter>D=HIT"

        #send my Hit or Miss Decision to the Game Engine Server
        print "queryLocator at side " + network_side + " print: Sending"+decision

        # Modified by Chen Binbin to use Tcp
        self.sock_ge.send(decision)

        # self.sock.sendto(decision,self.addrGE)

QueryLocator = QueryLocator()
