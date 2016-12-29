#!/usr/bin/env  python2.3

"""
Created by Fang Hui 2004.11 fh2008@hotmail.com
"""

import os
import sys
#import pygtk
import gtk
import gtk.gdk
import gobject
import math
import string
import time
import socket
import random
import thread
from configure import *

network_mode = "UDP"    # the way GUI communicates with Location


#differentiate the ports in case two sites' code run on the same machine

if "MIT" == network_side:
    port_location_0 = port_gui0_location0
    port_location_1 = port_gui0_location1

else:
    port_location_0 = port_gui1_location0
    port_location_1 = port_gui1_location1



class NetHandler:
    def __init__(self):
        self.callback_functions = []
        self.line_remainder=""
        self.location_sock = range(2)
  
    def register_callback(self, callback_func):
       self.callback_functions.append(callback_func)

    def setup_network(self) :
       
       self.setup_game_engine( host_game_engine, port_game_engine )
       
       if "MIT" == network_side:
           self.accept_location( localhost, port_location_0, 0 )
       else:
           self.request_location( host_game_engine, port_location_0, 0 )
           # assume site 0's master locator and game engine same IP
                             
       self.accept_location( localhost, port_location_1, 1 )



    def accept_location(self ,host, port, i): 

       print "gui at side " + network_side + " print: listening on port %d" % port       
       if network_mode == "TCP" :
         try : self.location_sock[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         except socket.error :
           print "gui at side " + network_side + " print: socket error"

         try: self.location_sock[i].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         except socket.error :
           print "gui at side " + network_side + " print: setsocketopt error"

         try :  self.location_sock[i].bind( ( host, port) )
         except socket.error :
           print "gui at side " + network_side + " print: bind error"

         try : self.location_sock[i].listen(5)
         except socket.error :
           print "gui at side " + network_side + " print: listen error"

         (self.nus_client_sock, address) = self.location_sock[i].accept()
         print "gui at side " + network_side + " print: Incoming connection from %s:%d\n" % (address[0], address[1])
         
       else : # UDP
         self.location_sock[i] = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
         self.location_sock[i].bind( ( host,port) )
         data = self.location_sock[i].recv(1024)
         print "gui at side " + network_side + " print: receive " + data


       try:
           if i == 0:
               gtk.input_add( self.location_sock[i],    gtk.gdk.INPUT_READ, self.read_location_daemon0)
           elif i == 1:
               gtk.input_add( self.location_sock[i],    gtk.gdk.INPUT_READ, self.read_location_daemon1)
       except gtk.gdk.INPUT_EXCEPTION : print "gui at side " + network_side + " print: input_add error"
         

    def request_location(self ,host, port, i): 
       
       if network_mode == "TCP" :

          self.location_sock[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          ready = 0

          while  not ready :
            #print "."
            try:
              self.location_sock[i].connect(( host,port))
              ready = 1
            except socket.error :
              ready = 0               

            #if not ready :
             #  time.sleep(2)

       
    #       try: gtk.input_add( self.mit_server_sock,    gtk.gdk.INPUT_READ, self.read_mit_server)
    #       except gtk.gdk.INPUT_EXCEPTION : print "input_add error"
       elif network_mode == "UDP" :
          self.location_sock[i] = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

          loop = 1

          while loop:
              print (host,port)
              self.location_sock[i].sendto( "Get started", (host_game_engine,16072) )
              print "GUI@nus trying MIT location server!"
              self.location_sock[i].settimeout(0.5)
              try:
                  data = self.location_sock[i].recv(1024)
                  loop = 0
              except:
                  loop = 1
                  #print "resending"
              
          #print "gui at side " + network_side + " print: receive from location" + str(i) + ", data: " + data
          
       try:
           if i == 0:
               gtk.input_add( self.location_sock[i],    gtk.gdk.INPUT_READ, self.read_location_daemon0)
           elif i == 1:
               gtk.input_add( self.location_sock[i],    gtk.gdk.INPUT_READ, self.read_location_daemon1)

       except gtk.gdk.INPUT_EXCEPTION : print "gui at side " + network_side + " print: input_add error"   
      

    def setup_game_engine(self ,host, port):    
       self.game_engine_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       ready = 0
       while  not ready :
           #print "."
           try:
              self.game_engine_sock.connect(( host, port))
              ready = 1
              self.game_engine_sock.send("Connected by gui from site " + network_side)
           except socket.error :
              ready = 0               

           #if not ready :
            #  time.sleep(1)

       print "GUI  at side " + network_side + " print: Now connected to game engine"

       try: gtk.input_add( self.game_engine_sock, gtk.gdk.INPUT_READ, self.read_game_engine)        
       except gtk.gdk.INPUT_EXCEPTION : print "gui at side " + network_side + " print: input_add error"
       



    def read_location_daemon0(self,source,condition) :
       
       if network_mode == "TCP" :
         data = source.recv(1024)
         self.parse_msg_loc(0,data)
       else :
         data,addr = source.recvfrom(1024)
         print "GUI @" + network_side + " Rcv from MIT location: " + data # + str(addr)
         self.parse_msg_loc(0,data)

       try: gtk.input_add( self.location_sock[0],    gtk.gdk.INPUT_READ, self.read_location_daemon0)
       except gtk.gdk.INPUT_EXCEPTION : print "gui at side " + network_side + " print: input_add error"   


    def read_location_daemon1(self,source,condition) :
       
       if network_mode == "TCP" :
         data = source.recv(1024)
         self.parse_msg_loc(0,data)
       else :
         data,addr = source.recvfrom(1024)
         print "GUI @" + network_side + " Rcv from NUS location: " + data  #+ str(addr)
         self.parse_msg_loc(1,data)

       try: gtk.input_add( self.location_sock[1],    gtk.gdk.INPUT_READ, self.read_location_daemon1)
       except gtk.gdk.INPUT_EXCEPTION : print "gui at side " + network_side + " print: input_add error"   


    def  read_game_engine(self, sock, condition ):
       data = sock.recv(1024)
       print "GUI @" + network_side + " Recv from game engine:" + data
       self.parse_msg_game_engine(2,data)

       try: gtk.input_add( self.game_engine_sock, gtk.gdk.INPUT_READ, self.read_game_engine)        
       except gtk.gdk.INPUT_EXCEPTION : print "gui at side " + network_side + " print: input_add error"

    def  parse_msg_loc(self, source, line ) :

        if not line: return              
        
        #line = line[1:-1]               
        lines = self.line_remainder + line
        lines = string.split(lines, '\n')
        for line in lines[:-1]:
            z = string.split(line ,',')  #split by coma ','
            if len ( z ) == 1 :   
                ball_block = int (z[0])
                # print ball_block
                self.callback_functions[2](ball_block)
            else  :
                (x2 , y2 ) = ( int(z[0]), int(z[1]) )
                # print x2
                # print y2  
                (x , y ) = ( int(z[0]), int(z[1]) )                
                #x, y = self.transform(x,y)
                if source == 0 or source == 1: #location
                   self.callback_functions[0](source,x,y)
                else :  # score
                   self.callback_functions[1](x,y)

        self.line_remainder = lines[-1]



    def  parse_msg(self, source, line ) :

        if not line: return              
        
        #line = line[1:len(line)-2]               
        lines = self.line_remainder + line
        lines = string.split(lines, '\n')
        for line in lines[:-1]:

            z = string.split(line ,',')  #split by coma ','
            if len ( z ) == 1 :   
                ball_block = int (z[0])
                # print ball_block
                self.callback_functions[2](ball_block)
            else  :
                zx =  z[0][1:-1]
                zy =  z[1][0:-1]
                # print zx
                # print zy  
                (x2 , y2 ) = ( int(zx), int(zy) )
                (x , y ) = ( int(z[0]), int(z[1]) )                
                #x, y = self.transform(x,y)
                if source == 0 or source == 1: #location
                   self.callback_functions[0](source,x,y)
                else :  # score
                   self.callback_functions[1](x,y)

        self.line_remainder = lines[-1]


    def  parse_msg_game_engine(self, source, line ) :

        if not line: return              
        
        #line = line[1:-1]               
        lines = self.line_remainder + line
        lines = string.split(lines, '\n')
        for line in lines[:-1]:
            z = string.split(line ,',')  #split by coma ','
            if len ( z ) == 1 :   
                ball_block = int (z[0])
                # print ball_block
                self.callback_functions[2](ball_block)
            else  :
                (x2 , y2 ) = ( int(z[0]), int(z[1]) )
                # print x2
                # print y2  
                (x , y ) = ( int(z[0]), int(z[1]) )                
                #x, y = self.transform(x,y)
                if source == 0 or source == 1: #location
                   self.callback_functions[0](source,x,y)
                else :  # score
                   self.callback_functions[1](x,y)

        self.line_remainder = lines[-1]

    def  idle(self) :
        #str = "Time:%d" % ( time.time() )
        #self.status.set_text(str)
        #duration = time.time() - self.time
        return  1

