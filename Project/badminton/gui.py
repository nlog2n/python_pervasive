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

import nethandler

from configure import *

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
      self.background = gtk.gdk.pixbuf_new_from_file("pictures/court.jpg")
      self.w, self.h = ( self.background.get_width(), self.background.get_height() )
      self.canvas.set_size_request( self.w, self.h )
      self.background.render_to_drawable(self.canvas.window,self.gc,0, 0, 0, 0, self.w, self.h, 0, 0, 0)
      
      self.player1_pic = gtk.gdk.pixbuf_new_from_file("pictures/p1.gif")
      self.player2_pic = gtk.gdk.pixbuf_new_from_file("pictures/p2.gif")      
      self.ball_pic    = gtk.gdk.pixbuf_new_from_file("pictures/ball5.gif")

      ######################################
      
      # create some graphics contexts to use for drawing
      self.radius = 5      
      self.brush_ball = self.canvas.window.new_gc()
      self.brush_ball_color = self.colormap.alloc_color("green")
      self.brush_ball.set_foreground( self.brush_ball_color )

      self.brush_player = self.canvas.window.new_gc()
      self.brush_player_color = self.colormap.alloc_color("red")
      self.brush_player.set_foreground( self.brush_player_color )


      self.player1 = self.wTree.get_widget("Player1")
      self.player2 = self.wTree.get_widget("Player2")      
      self.status  = self.wTree.get_widget("Status")            
#      self.player1.set_text("Player1:xxxx score:00")
#      self.player2.set_text("Player2:xxxx score:00")      

      
      
      self.p1x  = 185
      self.p1y  = 106
      self.p1_block = -5
      self.p2x  = 495
      self.p2y  = 184
      self.p2_block = 5
      
      self.ball_block = 5
      self.ball_x, self.ball_y = self.compute_ball_location( self.ball_block )

      self.ball_fall_x , self.ball_fall_y = (self.ball_x , self.ball_y )
      self.hightlight_finished = 1      
            
      self.score1 = 0
      self.score2 = 0

      self.show_score()
      self.status.set_text("Not started")
      
    
      dic = { 
              "on_drawingarea1_expose_event" :    self.on_drawingarea1_expose_event,  # redraw area
              "on_exit" : (gtk.mainquit)
             }
      self.wTree.signal_autoconnect(dic)
      
      self.network_ready = False
      self.map =  { 
-9:[102,128],
-8:[152,97],
-7:[195,60],
-6:[153,150],
-5:[198,116],
-4:[230,78],
-3:[221,148],
-2:[254,115],
-1:[296,66],
1:[308,179],
2:[327,135],
3:[409,78],
4:[420,215],
5:[447,132],
6:[484,89],
7:[531,225],
8:[563,166],
9:[560,90] }


      self.map_more_mesh =  { 
-16:[73,139],
-15:[101,120],
-14:[147,86],
-13:[177,61],
-12:[110,148],
-11:[144,120],
-10:[169,95], 
-9:[216,64],
-8:[170,152],
-7:[198,120],
-6:[228,98],
-5:[251,70],
-4:[210,153],
-3:[232,129],
-2:[265,96],
-1:[294,67],
1:[284,175],
2:[302,153],
3:[335,117],
4:[366,78],
5:[360,186],
6:[358,152],
7:[398,118],
8:[417,86],
9:[440,195],
10:[469,173],
11:[454,127],
12:[495,96],
13:[527,221],
14:[537,193],
15:[541,146],
16:[562,101] }


   def show_score(self) :
#      str1 = "Player1:"+str(self.p1x)+","+str(self.p1y)+"  score:"+str(self.score1)
#      str2 = "Player2:"+str(self.p2x)+","+str(self.p2y)+"  score:"+str(self.score2)
      str1 = "MIT Player:"+"  score:"+str(self.score1)
      str2 = "NUS Player:"+"  score:"+str(self.score2)

      self.player1.set_text(str1)
      self.player2.set_text(str2)      
      self.status.set_text("Started")

   def get_block(self, block) :
     pic_x , pic_y = ( self.map[block][0],self.map[block][1] )
     return (pic_x , pic_y )             
   
   def on_drawingarea1_expose_event(self, widget, event):
            self.draw()

   def draw(self) :
        self.background.render_to_drawable(self.canvas.window,self.gc,0, 0, 0, 0, self.w, self.h, 0, 0, 0) 
        
        #self.ball_block = random.choice([1, 2, 3, 4, -1,-2,-3,-4,-5])

        #( bx , by ) = self.compute_ball_location( self.ball_block )
        self.draw_icon2(0, self.ball_x,self.ball_y)
        self.draw_icon2(1, self.p1x,self.p1y)
        self.draw_icon2(2, self.p2x,self.p2y)
        self.show_score()
        self.draw_hightlight()  # added dec13 @fh
        

   def  draw_hightlight(self ) :
       for  block in [1,2,3,4,5,6,7,8,9,-1,-2,-3,-4,-5,-6,-7,-8,-9] :
           #(bx , by )  = self.compute_ball_location(block)
           (bx,  by )  = self.get_block(block)            
           self.draw_icon(0,bx,by)
       
       if not self.hightlight_finished :
       	   self.draw_hightlight_ball_fall( self.ball_fall_x, self.ball_fall_y )

           
   def  draw_hightlight_ball_fall(self , x, y ) :           
       x1 = x - self.radius
       y1 = y - self.radius

       self.brush_ball.set_foreground( self.colormap.alloc_color("red") )

       w1 = self.radius * 2
       h1 = self.radius * 2
       self.canvas.window.draw_arc( self.brush_ball, gtk.TRUE, x1, y1, w1, h1,0, 360*64 )
       
       self.brush_ball.set_foreground(self.colormap.alloc_color("green"))
       return


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
       
   def draw_icon2(self, icon , x, y ) :
      
       if  icon == 0 : # ball
             pixbuf = self.ball_pic
       elif icon == 1 :  # player 1
             pixbuf = self.player1_pic
       else  :
             pixbuf = self.player2_pic
             
       (w,h ) =   ( pixbuf.get_width(), pixbuf.get_height() )
       pixbuf.render_to_drawable(self.canvas.window,self.gc, 0,0, x- w/2, y- h/2,  -1, -1, 0, 0, 0)        
   
   def  transform(self,w ,h ) :
      
      x, y = ( h, w)
      
      #print  x
      #print y
      x1 = (39*(1-x/13.4)+577*x/13.4)*(1-y/5.2) + (156*(1-x/13.4)+600*x/13.4)*y/5.2 
      y1 = (143*(1-y/5.2)+67*y/5.2)*(1-x/13.4) + (255*(1-y/5.2)+116*y/5.2)* x/13.4
      #print x1
      #print y1
      return ( int(x1), int(y1) )
   
   
   def  compute_ball_location(self, block) :
       
       block = - block
       
       if block > 0 :
             block = block - 1 
             ( rw , rh ) = ( block % 3 , block / 3 )
             rh = rh + 4
             rw = rw + 1
       else  :
             block = block + 9
             ( rw , rh ) = ( block % 3 , block / 3 )
             rw = rw + 1
             rh = rh + 1
       
       wid , hei = ( 5.2 , 13.4 )
       ( block_w , block_h )  = ( wid / 3 , hei / 6 )
       
       #return ( int((rw - 0.5)*block_w),int((rh - 0.5)*block_h))
       w, h  = ( ((rw - 0.5)*block_w),((rh - 0.5)*block_h))
       w, h =  ( 5.2 - w , 13.4 - h )
       ( ballx , bally ) = self.transform(w,h)
       return (ballx, bally)

   # Modification Dec,13
   # add the location(x,y) check on rectangle 670*520 @fh
   def  get_location(self, source, msg_x, msg_y) :

        if msg_x <0 :     msg_x = 0
        if msg_x > 670 :  msg_x = 670
        if msg_y <0 :     msg_y = 0
        if msg_y > 520 :  msg_y = 520
        
        ix  = msg_x *3 / 670
        iy  = msg_y *3 / 520
        if ix >= 3 : ix = 2
        if iy >= 3 : iy = 2
        idx = ix + iy * 3 + 1

        if  source == 1 : #left
             idx = -idx
        else :
             idx = idx 
        if  idx < int(-9)  : idx = int(-5)
        if  idx > 9  : idx = 5
        
        a = self.map[idx]
        ax , ay  = ( a[0], a[1])   
        return (ax, ay)

   def  get_location_more_mesh(self, source, msg_x, msg_y) :
        if msg_x <0 :     msg_x = 0
        if msg_x > 670 :  msg_x = 670
        if msg_y <0 :     msg_y = 0
        if msg_y > 520 :  msg_y = 520
        
        ix  = msg_x *4 / 670
        iy  = msg_y *4 / 520
        if ix >= 4 : ix = 3
        if iy >= 4 : iy = 3
        idx = ix + iy * 4 + 1

        if  source == 1 : #left
             idx = -idx
        else :
             idx = idx 
        if  idx < int(-16)  : idx = int(-16)
        if  idx > 16  : idx = 16
        
        a = self.map_more_mesh[idx]
        ax , ay  = ( a[0], a[1])   
        return (ax, ay)


   # use the mesh match method
   def  activate_location(self, msg_source,msg_x, msg_y ) :

        if msg_source == 1 :
                #self.p1x , self.p1y = self.get_location(msg_source,msg_x,msg_y)           
                #self.p1x , self.p1y = self.get_location_more_mesh(msg_source,msg_x,msg_y)           
                self.p1x , self.p1y = self.get_location_more_mesh(msg_source,msg_y,msg_x)           
                #self.draw_icon2(1, self.p1x,self.p1y)                
        else :  #MIT
                #self.p2x , self.p2y = self.get_location(msg_source,msg_x,msg_y)
                #self.p2x , self.p2y = self.get_location_more_mesh(msg_source,msg_x,msg_y)
                self.p2x , self.p2y = self.get_location_more_mesh(msg_source,msg_y,msg_x)
                #self.draw_icon2(2, self.p2x,self.p2y)                

        self.draw()  
              
        return

    
   # use the plane transform function
   def  activate_location2(self, msg_source,msg_x, msg_y ) :
        # print "gui.py at side " + network_side + " print: act location"

        (msg_x, msg_y)  =  (msg_y/100 , msg_x/100)
        
        if msg_source == 1 : # left side 
                h , w = (6.70 - msg_x ,   5.20 - msg_y )
                
                #h, w  = ( h -0.2 , w + 0.2 ) # adjust
        else :
                h, w  = ( 6.70 + msg_x , msg_y )
                
                #h, w  = ( h +0.1 , w + 0.2 ) # adjust                

        (w2 , h2 ) = self.transform(w,h)                        
        
        if msg_source == 1 :
                self.p1x , self.p1y = (w2 , h2 )           
                #self.draw_icon2(1, self.p1x,self.p1y)                
        else :  #MIT
                self.p2x , self.p2y = (w2 , h2 )                     
                #self.draw_icon2(2, self.p2x,self.p2y)                
        print  "gui.py at side " + network_side + " print:" + (w2,h2)
        self.draw()  


               
        return
        
   def  activate_score(self, msg_x, msg_y ) :     
        # print "gui.py at side " + network_side + " print: act score"
        self.score1 , self.score2 = (msg_x , msg_y )                   
        self.show_score()
        return     

   # added dec13 @fh for delay the updation of ball trajectory
   def  delay_show(self,old_x,old_y,new_x,new_y,interval) :

        self.draw_hightlight_ball_fall(new_x, new_y)  # added dec13 @fh
        
        old_y = self.h - old_y
        new_y = self.h - new_y
        
        dx,dy = ( ( new_x - old_x ) / 5.0 , ( new_y - old_y ) / 5.0 )
        ox, oy = ( old_x/ 1.0 , old_y/ 1.0 )
        i = 0
        while  i < 5 : 
            ox = ox + dx
            oy = oy + dy
            i = i+1
            time.sleep(interval)  #  time = t/speed
            self.draw_icon2(0, int(ox), int(self.h - oy))

        self.ball_x , self.ball_y   = ( new_x,new_y )
        self.hightlight_finished = 1 # finished hightlight
        self.draw()        
        return    	


   def  activate_ball_delay(self, ball_block ) :

        old_block  = self.ball_block
        old_x ,old_y  = ( self.ball_x , self.ball_y )
        
        new_block  =  ball_block
        #self.ball_x , self.ball_y = self.compute_ball_location( self.ball_block )
        new_x , new_y = self.get_block(new_block)
        self.ball_fall_x , self.ball_fall_y = (new_x, new_y )
        
        self.hightlight_finished = 0  # start hightlight
        thread.start_new_thread(self.delay_show, (old_x,old_y,new_x,new_y,0.2) )
       
#        self.draw()
        return


   def  activate_ball(self, ball_block ) :

        old_block  = self.ball_block
        old_x ,old_y  = ( self.ball_x , self.ball_y )
        
        self.ball_block = ball_block
        #self.ball_x , self.ball_y = self.compute_ball_location( self.ball_block )
        self.ball_x , self.ball_y  = self.get_block(ball_block) 
        self.draw_hightlight_ball_fall(self.ball_x, self.ball_y)  # added dec13 @fh
        
        old_y = self.h - old_y
        
        new_x , new_y = (self.ball_x , self.ball_y)
        new_y = self.h - new_y
        
        dx,dy = ( ( new_x - old_x ) / 5.0 , ( new_y - old_y ) / 5.0 )
        ox, oy = ( old_x/ 1.0 , old_y/ 1.0 )
        i = 0
        while  i < 5 : 
            ox = ox + dx
            oy = oy + dy
            i = i+1
            time.sleep(0.2)  #  time = t/speed
            self.draw_icon2(0, int(ox), int(self.h - oy))

        self.draw()
        return


  
######################### Main Entrance##################################################
if __name__=="__main__":
  
        app = gui()

        conn = nethandler.NetHandler()
        conn.register_callback(app.activate_location)
        #conn.register_callback(app.activate_location2)        
        conn.register_callback(app.activate_score)                
        conn.register_callback(app.activate_ball)                        
        conn.setup_network()
        
        #try: gtk.input_add( conn.center_server_sock, gtk.gdk.INPUT_READ, conn.read_center_server)        
        #except gtk.INPUT_EXCEPTION : print "input_add error"
 
        #try: gtk.input_add( conn.mit_server_sock,    gtk.gdk.INPUT_READ, conn.read_mit_server)
        #except gtk.INPUT_EXCEPTION : print "input_add error"
               
        #gtk.idle_add( conn.idle)
        
        gtk.main()   
        
        while (0) :
             while gtk.events_pending() :
                    gtk.main_iteration()
             if conn.mit_server_ready == 0  : 
                 conn.read_mit_server(conn.mit_server_sock,gtk.gdk.INPUT_READ)                    
             if conn.center_server_ready == 0  : 
                 conn.read_center_server(conn.center_server_sock,gtk.gdk.INPUT_READ)                                             
             if conn.my_server_ready == 0  : 
                 conn.read_my_server(conn.nus_client_sock,gtk.gdk.INPUT_READ)                            
             if conn.my_server2_ready == 0  : 
                 conn.read_my_server2(conn.mit_client_sock,gtk.gdk.INPUT_READ)                            
       
