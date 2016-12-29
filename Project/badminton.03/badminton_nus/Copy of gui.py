#!/usr/bin/env  python2.3

"""
Created by Fang Hui 2004.11 fh2008@hotmail.com
"""

import os
import sys
import pygtk
import gtk
import gtk.glade
import gtk.gdk
import gobject
import math
import pango
import string
import time
import socket
import random
import thread

class gui:
  
   def __init__(self):


      self.wTree=gtk.glade.XML ("gui.glade") 

      ######################################
      # get the drawing area attributes from top window
      self.canvas =  self.wTree.get_widget("drawingarea1")
      self.style = self.canvas.get_style()
      self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
      self.pangolayout = self.canvas.create_pango_layout("")         
      self.colormap = self.canvas.get_colormap()

      # get image pix buffer from image file
      self.basepixbuf = None
      self.currentpixbuf = None
      self.mapfile  = "maps/tennis_ground5.png"
      self.basepixbuf = gtk.gdk.pixbuf_new_from_file(self.mapfile)
      self.w, self.h = ( self.basepixbuf.get_width(), self.basepixbuf.get_height() )
      self.canvas.set_size_request( self.w, self.h )
      self.currentpixbuf = self.basepixbuf
      self.currentpixbuf.render_to_drawable(self.canvas.window,self.gc,0, 0, 0, 0, self.w, self.h, 0, 0, 0)
      ######################################
      
      # create some graphics contexts to use for drawing
      self.radius = 5      
      self.brush_ball = self.canvas.window.new_gc()
      self.brush_ball_color = self.colormap.alloc_color("blue")
      self.brush_ball.set_foreground( self.brush_ball_color )

      self.brush_player = self.canvas.window.new_gc()
      self.brush_player_color = self.colormap.alloc_color("red")
      self.brush_player.set_foreground( self.brush_player_color )


      self.player1 = self.wTree.get_widget("Player1")
      self.player2 = self.wTree.get_widget("Player2")      
      self.status  = self.wTree.get_widget("Status")            
      self.player1.set_text("Player1:xxxx score:nnnn")
      self.player2.set_text("Player2:xxxx score:nnnn")      
      self.status.set_text("Status: ")
      
      
      self.p1x  = 100
      self.p1y  = 200
      self.p2x  = 230
      self.p2y  = 355
      
      self.ball_block = 5
            
      self.score1 = 0
      self.score2 = 0
      
    
      dic = { 
              "on_drawingarea1_expose_event" :    self.on_drawingarea1_expose_event,  # redraw area
              "on_exit" : (gtk.mainquit)
             }
      self.wTree.signal_autoconnect(dic)
       

   
   def on_drawingarea1_expose_event(self, widget, event):
            self.draw()

   def draw(self) :
        current_w, current_h = ( self.currentpixbuf.get_width(), self.currentpixbuf.get_height() )
        self.currentpixbuf.render_to_drawable(self.canvas.window,self.gc,0, 0, 0, 0, current_w, current_h, 0, 0, 0) 
        
        #self.ball_block = random.choice([1, 2, 3, 4, -1,-2,-3,-4,-5])

        ( ballx , bally ) = self.compute_ball_location( self.ball_block )
        self.draw_icon(0, ballx, bally)
        self.draw_icon(1, self.p1x,self.p1y)
        self.draw_icon(2, self.p2x,self.p2y)        

   def  draw_icon(self, icon, x, y ) :

       x1 = x - self.radius
       y1 = y - self.radius

       if  icon == 0 :# ball
          w1 = self.radius * 2
          h1 = self.radius * 2
          self.canvas.window.draw_arc( self.brush_ball, gtk.TRUE, x1, y1, w1, h1,0, 360*64 )
          return
          
       elif icon == 1 : # player 1
          name = "Player 1"
       elif icon == 2 :# player 2
          name = "Player 2"

       brush = self.brush_player          
       layout = self.pangolayout 
       layout.set_text( name )
       lw,lh = layout.get_pixel_size()
       lx =int( x1 - lw / 2 )
       ly =int( y1 - lh / 2 )
       self.canvas.window.draw_layout(brush, lx, ly, layout)
       

   def  compute_ball_location(self, block) :
       if block > 0 :
             ( rw , rh ) = ( block % 3 , block / 3 )
             rh = rh + 4
       else  :
             block = block + 10     
             ( rw , rh ) = ( block % 3 , block / 3 )
       
       ( block_w , block_h )  = ( self.w / 3 , self.h / 6 )
       
       return ( int((rw - 0.5)*block_w),int((rh - 0.5)*block_h))


   def init_server(self ) : # create the server socket
      self.gui_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      port =  8010
  
      # allow the socket to be re-used immediately after a close
      self.gui_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      self.gui_server_sock.bind( ("0.0.0.0", port) )
      
      # start the server socket
      self.gui_server_sock.listen(5)
      print "waiting for new connection on port %d" % port

   # only recv
   def  handle_server(self, sock, condition ) :
         (client, address) = s.accept()
         print "accepted connection from %s:%d\n" % (address[0], address[1])

         data = client.recv(1024)
         if len(data) == 0 :
             print "\n\nconnection with %s closed." % address[0]

         sys.stdout.write(data)

   
   def  init_client(self, ip_loc,port ): 

        # Open socket to get data
        self.gui_client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.gui_client_sock.connect((ip_loc, port))
        print "connect OK"
        #self.socket1.send("r\n")

   # only recv
   def  handle_client(self, sock, condition )  :
        line = sock.recv(1024)
        if not line: return                     
        print line

        z = string.split(line ,',')  #split by coma ','
        if len ( z ) == 1 :
        	 if len ( z[0] ) >=2 and ( z[0][0] == 'S' or z[0][0] == 's' ) :
        	 	  score = int ( z[0][1:] )
        	 	  if sock == self.gui_client_sock :
        	 	  	   self.p1s = score 
        	 	  else :
        	 	  	   self.p2s = score
           else :
           	  self.ball_block = int (z[0])
        else  :
           (x , y ) = ( int(z[0]), int(z[1]) )
           if  sock == self.gui_client_sock:
              ( self.p1x , self.p1y ) = (x,y)
           else  : 
              ( self.p2x , self.p2y ) = (x,y)
       
        self.draw()        
        return 0

          
   def  idle(self) :
        #str = "Time:%d" % ( time.time() )
        #self.status.set_text(str)
        #duration = time.time() - self.time
        return 



   def setup_network(no,interval):   
       while True:
       print 'Thread :(%d) Time:%s'%(no,time.ctime())
       time.sleep(interval)
   
   def test():
      thread.start_new_thread(timer,(1,1))
      thread.start_new_thread(timer,(2,3))
        
######################### Main Entrance##################################################
if __name__=="__main__":
  
        app = gui()
        
        thread.start_new_thread(setup_network,(host,port) )
        thread.start_new_thread(setup_network,(host,port) )        

        app.init_client("sunfire.comp.nus.edu.sg",8009)
        gtk.input_add(app.gui_client_sock, gtk.gdk.INPUT_READ, app.handle_client)
        gtk.idle_add( app.idle)

        gtk.main()
        
                    
