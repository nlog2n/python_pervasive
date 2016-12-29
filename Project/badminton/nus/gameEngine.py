#!/usr/bin/env python 
"""
Badminton game engine, by: Chen Binbin
"""

import socket
import random
from random import Random, random
import math
from configure import *

# static
BALLSPEED = 0.3

# Initialize all the sockets: location, speech, GUI port for both sites

# Arbitrary non-privileged port for two sides,
# but need to be configured in all components in advance
# 16069 is a good port not being blocked


class server:
    def __init__(self):
        print network_side + " initialize game engine"
        self.conn_gui = range(2)
        self.conn_speech = range(2)
        self.conn_location = range(2)

        # Assume all components connect to central server's port 16069.
        # And send a msg identifies themselves

        # Note: it maybe helpful to inform components other components' address to facilitate their interconnection


        try : self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error :
            print "Game Engine print: socket.socket error"

        try: self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error :
            print "Game Engine print: setsocketopt error"
    
        try: self.sock.bind(addrGE)
        except socket.error :
            print "Game Engine print: bind error"

        try: self.sock.listen(1)
        except socket.error :
            print "Game Engine print: listen error"
            
        
        for iterator in range(4):   # Here ignores speech daemon here, otherwise change 4 to 6
            
            conn, addr = self.sock.accept()
            msg = conn.recv(1024)

            print "Game Engine print: " + msg

            if '0' in msg or 'mit' in msg.lower():
                i = 0
            else:
                i = 1

            if "location" in msg.lower():
                self.conn_location[i] = conn
                
            elif "gui" in msg.lower():
                self.conn_gui[i] = conn
                
            elif "speech" in msg.lower():
                self.conn_speech[i] = conn
                if "error" in msg.lower():
                    self.speech_up[i] = 0
                else:
                    self.speech_up[i] = 1
            
        print "Game Engine print: All connected"

    def new_game(self):
           
        # Waiting for both sides to enter a new game

        for i in range(2):
            while 1:
                '''if self.speechup[i] == 1:
                    data = self.conn_speech[i].recv(1024)
                    print "Received from speech" + data
                else:'''

                data = raw_input("wait here")
                print "Game engine raw input get: " + data
                # data = raw_input("enter stop or new to represent palyer " + str(i))
                if "stop" in data.lower():
                    return
                else:
                    break

        # randomly decide which one serves first
        server_player = 0
        client_player = 1
        U = random()
        if   U < 0.5:
            server_player, client_player = client_player, server_player

        # location is given by:

        ###net### 
        # _____ # 
        # 1 2 3 # 
        # 4 5 6 # 
        # 7 8 9 # 
        # ----- # 
        #  end  #

        # use corresponding negative number when shuttlecock at opponent's half court


        score = [0,0]

        # loop of game, 3 points to win
        
        while score[server_player] < 3:
            
            ballPosition = 5
            distance = 0
            
            # update service player and ball position

            print "Game Engine print: Player " + str(server_player) + " serve first."

            # print " Using speech to send out who serve"
            # self.conn_speech[server_player].send("You serve\n")
            # self.conn_speech[client_player].send("Your opponent serve\n")

            print "Game Engine print: Using gui to send out score and ball position"
            self.conn_gui[server_player].send(str(score[0]) + "," + str(score[1]) + "\n" + str(ballPosition) + "\n")
            self.conn_gui[client_player].send(str(score[0]) + "," + str(score[1]) + "\n" + str(-ballPosition) + "\n")

            # get client site's ready command
            while 1:
                '''print "speech waits for player " + str(client_player) + " ready command"
                if self.speechup[client_player] == 1:
                    data = self.conn_speech[client_player].recv(1024)
                else:
                '''

                data = raw_input("Enter stop or ready (represent palyer " + str(client_player) + " 's speech")
            
                # for stop, should inform the other site!!!
                if "stop" in data.lower():
                    return
                else:
                    break

            sp = server_player   # server and client for current ball hit
            cp = client_player
            init = 0
            
            #loop of hitting ball
            while 1:
                
                

                """ speech part ignored
                # get the serving site's command on the shuttlecock's destination
                # after first serve, all other serve should have a timeout limit. Revise later!!!
                print "speech waits for player " + str(sp) + " ball destination"
                data = self.conn_speech[sp].recv(1024)
                print data
                    
                if data.find("stop") != -1:
                    return
                if data.isdigit():
                    n = int(data)
                """
                    
                        
                if init == 0:
                    init = 1

                # Randomly generate the ball position
                n = int(random()*9 + 1)

                distance = math.sqrt(pow(n/3 + ballPosition/3 + 1, 2) + pow(n%3 - ballPosition%3, 2))
                ballPosition = n

                # update client and server's ball position accordingly
                print "Game Engine print: use GUI socket to update ball position" + str(n)
                self.conn_gui[sp].send(str(-ballPosition) + "\n")
                self.conn_gui[cp].send(str(ballPosition) + "\n")

                # print "speech update client player " + str(cp) + " ball position"            
                # self.conn_speech[cp].send("Ball at " + str(ballPosition) + "\n")

                # inform location daemon the position and time the player should be at to return the ball

                print "Game Engine print: use location socket to tell player " + str(cp) + " to hit the ball at " + str(n) + " in " + str(distance * BALLSPEED) +  " seconds"
                self.conn_location[cp].send("T=" + str(distance * BALLSPEED) + "S=" + str(ballPosition) + "\n")

                print "Game Engine print: Location socket waits for player " + str(cp) + "  hit / miss result"
                # see whether client catch the ball or not
                data = self.conn_location[cp].recv(1024)
                print "Game Engine print: " + data
                
                        
                if "hit" in data.lower():
                    sp, cp = cp, sp
                else:
                    print "player " + str(cp) + " missed!"
                    if sp == server_player:
                        score[sp] = score[sp] + 1
                    else:
                        server_player, client_player = client_player, server_player # change the server
                    break
                
        print "Game Engine print: use gui socket to send out final score"
        self.conn_gui[server_player].send(str(score[0]) + "," + str(score[1]) + "\n")
        self.conn_gui[client_player].send(str(score[0]) + "," + str(score[1]) + "\n")

        # print "speech server send win/lost"
        # self.conn_speech[server_player].send("win\n")
        # self.conn_speech[client_player].send("lost\n")

    def quit(self):
 
        for i in range(2):
            self.conn_gui[i].close()

	    '''
	    self.conn_speech[i].close()
            self.s_speech[i].close()
            '''

            self.conn_location[i].close()
            self.sock.close()


######################### Main Entrance##################################################
if __name__=="__main__":

    app = server()
    app.new_game()
    app.quit()

    raw_input("press Enter to quit")




