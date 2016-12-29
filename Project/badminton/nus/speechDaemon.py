#!/usr/bin/env python 
"""
Author: Chuan, Deh Hui
This is the voice processing program for SMA 5508's final project
To send & receive speech commands to/from the central server
"""

# Use the galaxy.server library
import galaxy.server

#initialize connection to send files to path_finder
import socket 

#Use the regular expression module
import re
import time
from configure import *

class speech_interface:

    def __init__(self):
        print " Speech interface is running..."
        print " Choices are STOP, END, START, Good Bye, and numbers 1 - 9"

    def connect(self):
        print "Connecting Speech server..."
        self.failtoconnect = 1
        while self.failtoconnect == 1:
            # Initalize the server object
            try:
                self.server1 = galaxy.server.Server("galaxy.csail.mit.edu", 10376, "MIT_badminton2")
                # Actually connect to the Galaxy frame relay
                self.server1.connect()
            except socket.error:
                self.failtoconnect = 1	

            print "Connecting central server..."
            #Socket setup to central server (i.e. Game logic)
            #Remember to change the port number later
            self.central_server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.central_server.connect(addrGE)
            print "connected!"
            if self.failtoconnect == 1:
                self.central_server.send("Connected from speech daemon at site " + network_side + ". Galaxy error.");
                time.sleep(10)
            else:
                self.central_server.send("Connected from speech daemon at site " + network_side + ". Galaxy success");

    def voice_processing(self):
        # Use the active variable to quit if we get "STOP", "END" or "Good bye"
        active = 1

        print "Processing voice command..."
        while (active):
            # Look for an incoming message from the server

            # !!! Is it blocking or not?
            
            c = self.server1.handleMessage(0)
    
            # If we got a message (recognition result)
            if c:
                # Print out the frame
                print c.frame.toString()
                # Figure out the action
                action = c.frame.getAction()

                # The call_answered action means we just got a new connection
                if (action == 'call_answered'):
                    c.sb_reply('Please enter voice command')

                # Goodbye, END or STOP means close off the conversation
                elif (action == 'goodbye' or action == 'end' or action == 'stop'):
                    print "Ending the game"
                    c.sb_goodbye('Game ended thanks for playing')
                    self.central_server.send('stop')
                    #End, so escape from while loop
                    active = 0
                
                ############################################################
                # Anything after this point means we really got something  #
                ############################################################
                elif (action == 'start' or action == 'ready'):
                    mytext = c.frame.getText()
                    if mytext:
                        print "Sending ",mytext
                        self.central_server.send(mytext)
                
                    #else, nothing to do

        	
                # We don't deal with shuttlecock destination anymore

                # for simplicity, we don't use speech to announce anything now

                """
                else:
                    mytext = c.frame.getText()
                    #Look for a number if there is any
                    #Must correspond to 1 through 9 for the 9 dots on court

                    if mytext:                   
                        num_list = re.findall(r'[1-9]', mytext)
                        if len(num_list) != 0:
                            #Assumption, should just be a single digit number
			    print "Sending number = ", num_list[0]	
                      #      self.central_server.send(num_list[0])
                            #Hit or miss
                       #     data = self.central_server.recv(1024)
		#	    print "Receive ", data
                            c.sb_reply("Hit/Miss")

                    else:    
                        # Out of the domain of recognition specified in SpeechBuilder
                        # ---> Probably don't want to say this c.sb_reply('I have no idea what is happening')
                        # It will be taken care as a random event in the central server
                        self.central_server.send("Error")
                """


    def quit(self):
        #Close connection  
#        self.central_server.close()   
        self.server1.close()
         
    
if __name__=="__main__":
    app = speech_interface()
    app.connect()
    app.voice_processing()
    app.quit()

