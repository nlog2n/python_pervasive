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


network_side = "MIT"

network_mode = "TCP"





class NetHandler :
  
   def __init__(self):
       if network_side == "MIT" :
          print "This is GUI for MIT program!@fh"
          self.my_server_ready = 0
          self.mit_server_ready = 1
          self.center_server_ready = 0  # on
          self.my_server2_ready = 0  # for mit client
          
          self.host_center_server , self.port_center_server = ( "localhost",50001 )
          self.host_my_server_4_nus, self.port_my_server_4_nus = ( "localhost", 15002)
          self.host_my_server2_4_mit, self.port_my_server2_4_mit = ( "localhost", 15004)
          self.host_mit_server , self.port_mit_server = ( "localhost", 16002 )
          
       elif  network_side == "NUS" :
          print "This is GUI for NUS program!@fh"          
          self.my_server_ready = 0
          self.mit_server_ready = 0
          self.center_server_ready = 0  # on
          self.my_server2_ready = 1  # 

          self.host_center_server , self.port_center_server = ( "localhost",60001 )
          self.host_my_server_4_nus, self.port_my_server_4_nus = ( "localhost", 15002)
          self.host_my_server2_4_mit, self.port_my_server2_4_mit = ( "localhost", 15004)
          self.host_mit_server , self.port_mit_server = ( "localhost", 16002 )
        

       self.callback_functions = []

       self.line_remainder=""




       return 
  
   # MIT mode
  
   def register_callback(self,callback_func):
        self.callback_functions.append(callback_func)
   
   def setup_network(self) :
       
       self.setup_center_server( self.host_center_server, self.port_center_server)
       

       self.setup_my_server( self.host_my_server_4_nus , self.port_my_server_4_nus) 
                             
       self.setup_my_server2(self.host_my_server2_4_mit, self.port_my_server2_4_mit)
       
       self.setup_mit_server(self.host_mit_server , self.port_mit_server)
       #self.sample()

       
       
       
       
       
       
       #thread.start_new_thread(self.setup_my_server,("localhost",8128) )                      
       #thread.start_new_thread(self.setup_mit_server,("sunfire.comp.nus.edu.sg",8001) )
       #thread.start_new_thread(self.setup_center_server,("sunfire.comp.nus.edu.sg",8002) )        

    
    
    
   def sample(self) :
       print '>>>Trying to connect to MIT server!'
       self.mit_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       ready = 0

       try:
              self.mit_server_sock.connect(( "sunfire.comp.nus.edu.sg",81234))
              ready = 1
       except socket.error :
              ready = 0
              print "err"               

       if not ready :
           time.sleep(10)
           try:
              self.mit_server_sock.connect(( "sunfire.comp.nus.edu.sg",81234))
              ready = 1
           except socket.error :
              ready = 0
              print "err"               


       print "Now connected to MIT server"
       
       try: gtk.input_add( self.mit_server_sock,    gtk.gdk.INPUT_READ, self.read_mit_server)
       except gtk.INPUT_EXCEPTION : print "input_add error"
   
  
   def setup_my_server(self ,host, port):  
       if self.my_server_ready  : return

       print "Gui server for NUS listening port %d" % port       
       if network_mode == "TCP" :
         try : self.my_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
         except socket.error :
           print "socket error"

         try: self.my_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
         except socket.error :
           print "setsocketopt error"

         try :  self.my_server_sock.bind( ( host, port) )
         except socket.error :
           print "bind error"

         try : self.my_server_sock.listen(5)
         except socket.error :
           print "listen error"

         (self.nus_client_sock, address) = self.my_server_sock.accept()
         print "Incoming connection from %s:%d\n" % (address[0], address[1])
       
         try: gtk.input_add( self.nus_client_sock,    gtk.gdk.INPUT_READ, self.read_my_server)            
         except gtk.INPUT_EXCEPTION : print "input_add error"
         
       else : # UDP
         self.my_server_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
         self.my_server_sock.bind( ( host,port) )
         self.my_server_sock.sendto( "Get started", (host,port) )
         try: gtk.input_add( self.my_server_sock,    gtk.gdk.INPUT_READ, self.read_my_server)            
         except gtk.INPUT_EXCEPTION : print "input_add error"
         

   def setup_my_server2(self ,host, port):  
       if self.my_server2_ready  : return
       
       print "Gui server for MIT listening port %d" % port
       if network_mode == "TCP" :
          try : self.my_server2_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          except socket.error :
            print "socket error"

          try: self.my_server2_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
          except socket.error :
            print "setsocketopt error"

          try :  self.my_server2_sock.bind( ( host, port) )
          except socket.error :
            print "bind error"

          try : self.my_server2_sock.listen(5)
          except socket.error :
            print "listen error"

          (self.mit_client_sock, address) = self.my_server2_sock.accept()
          print "Incoming connection from %s:%d\n" % (address[0], address[1])
       
          gtk.input_add( self.mit_client_sock,    gtk.gdk.INPUT_READ, self.read_my_server2)            
          #except gtk.INPUT_EXCEPTION : print "input_add error"
       else  : # UDP 
          self.my_server2_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
          self.my_server2_sock.bind( ( host,port) )
          self.my_server2_sock.sendto( "Get started", (host,port) )
          gtk.input_add( self.my_server2_sock,    gtk.gdk.INPUT_READ, self.read_my_server2)            
          #except gtk.INPUT_EXCEPTION : print "input_add error"
        


   
   def setup_mit_server(self ,host, port):   
       if self.mit_server_ready  : return         
       
       
       if network_mode == "TCP" :
          print '>>>Trying to connect to MIT server!'

          self.mit_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          ready = 0

          while  not ready :
            #print "."
            try:
              self.mit_server_sock.connect(( host,port))
              ready = 1
            except socket.error :
              ready = 0               

            #if not ready :
             #  time.sleep(2)

          print "Now connected to MIT server"
       
#       try: gtk.input_add( self.mit_server_sock,    gtk.gdk.INPUT_READ, self.read_mit_server)
#       except gtk.INPUT_EXCEPTION : print "input_add error"
       elif network_mode == "UDP" :
          self.mit_server_sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)              
          gtk.input_add( self.mit_server_sock,    gtk.gdk.INPUT_READ, self.read_mit_server)
      

   def setup_center_server(self ,host, port):  
       if self.center_server_ready  : return  
       print '>>>Trying to connect to Center server on port %d' % port       
       self.center_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       ready = 0
       while  not ready :
           #print "."
           try:
              self.center_server_sock.connect(( host, port))
              ready = 1
           except socket.error :
              ready = 0               

           #if not ready :
            #  time.sleep(1)

       print "Now connected to center server"

       try: gtk.input_add( self.center_server_sock, gtk.gdk.INPUT_READ, self.read_center_server)        
       except gtk.INPUT_EXCEPTION : print "input_add error"
       


    
   def read_my_server(self,source,condition) :
       print "Rcv from NUS client"
       if network_mode == "TCP" :
         data = source.recv(1024)
         self.parse_msg_loc(0,data)
       else :
         data,addr = source.recvfrom(1024)
         self.parse_msg_loc(0,data)         

   def read_my_server2(self,source,condition) :
       print "Rcv from MIT client"
       if network_mode == "TCP" :       
         data = source.recv(1024)
         self.parse_msg_loc(1,data)
       else :
         data,addr = source.recvfrom(1024)
         self.parse_msg_loc(1,data)         



   # only recv
   def  read_mit_server(self, sock, condition )  :
     print " Recv from MIT server"
     if network_mode == "TCP" :
       data = sock.recv(1024)        
       self.parse_msg_loc(1,data)
     else :
       data , addr = sock.recvfrom(1024)
       self.parse_msg_loc(1,data)

   def  read_center_server(self, sock, condition )  :
     print " Recv from Center server"
     data = sock.recv(1024)        
     self.parse_msg_center_server(2,data)


   def  parse_msg_loc(self, source, line ) :
    
        if not line: return              
        
        #line = line[1:-1]               
        lines = self.line_remainder + line
        lines = string.split(lines, '\n')
        for line in lines[:-1]:
            z = string.split(line ,',')  #split by coma ','
            if len ( z ) == 1 :   
                ball_block = int (z[0])
                print ball_block
                self.callback_functions[2](ball_block)
            else  :
                (x2 , y2 ) = ( int(z[0]), int(z[1]) )
                print x2
                print y2  
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
                print ball_block
                self.callback_functions[2](ball_block)
            else  :
                zx =  z[0][1:-1]
                zy =  z[1][0:-1]
                print zx
                print zy  
                (x2 , y2 ) = ( int(zx), int(zy) )
                (x , y ) = ( int(z[0]), int(z[1]) )                
                #x, y = self.transform(x,y)
                if source == 0 or source == 1: #location
                   self.callback_functions[0](source,x,y)
                else :  # score
                   self.callback_functions[1](x,y)

        self.line_remainder = lines[-1]


   def  parse_msg_center_server(self, source, line ) :
    
        if not line: return              
        
        #line = line[1:-1]               
        lines = self.line_remainder + line
        lines = string.split(lines, '\n')
        for line in lines[:-1]:
            z = string.split(line ,',')  #split by coma ','
            if len ( z ) == 1 :   
                ball_block = int (z[0])
                print ball_block
                self.callback_functions[2](ball_block)
            else  :
                (x2 , y2 ) = ( int(z[0]), int(z[1]) )
                print x2
                print y2  
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
