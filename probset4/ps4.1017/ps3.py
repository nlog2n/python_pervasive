#!/usr/bin/env python
#
"""
Created by Fang Hui 2004.10 fh2008@hotmail.com
Platform: Debian Linux
Dev environment:   Python + pygtk + GTK/Glade
Goal : problem set 3 (search path problem GUI)
Functions:
  1. search path

  2. edit path
 add vertex: \tleft click somewhere
 clear vertex:\tright click on vertex
 move vertex: \tleft click on vertex, drag
 add edge: \tmiddle click first vertex, middle click second vertex
 name vertex: \tleft click on vertex, type name
"""

import os
import sys
import pygtk

#pygtk.require("2.0")
import gtk
import gtk.glade
import gtk.gdk
import gobject
import math
import pango
import string


import galaxy.server

import graph
import search  # A* search algo



class gui:

  
   def __init__(self):


      self.wTree=gtk.glade.XML ("graph.glade") #1

      # get the drawing area attributes from top window
      self.canvas =  self.wTree.get_widget("drawingarea1")
      self.style = self.canvas.get_style()
      self.gc = self.style.fg_gc[gtk.STATE_NORMAL]
      self.pangolayout = self.canvas.create_pango_layout("")         
      self.colormap = self.canvas.get_colormap()

      # get image pix buffer from image file
      self.map = self.wTree.get_widget("combo-entry1").get_text()
      self.basepixbuf = None
      self.currentpixbuf = None
      self.mapfile = "maps/"+ self.map + ".png"   
      if self.mapfile is not None and os.path.exists(self.mapfile):
            self.basepixbuf = gtk.gdk.pixbuf_new_from_file(self.mapfile)
            self.w, self.h = ( self.basepixbuf.get_width(), self.basepixbuf.get_height() )
            self.canvas.set_size_request( self.w, self.h )
            self.currentpixbuf = self.basepixbuf
            self.currentpixbuf.render_to_drawable(self.canvas.window,self.gc,0, 0, 0, 0, self.w, self.h, 0, 0, 0)


      #save frequently-used list
      self.srclist = []
      self.destlist= []


      self.graphfile = "graphs/"+self.map + ".graph"
      self.graph = graph.Graph()
      self.graph.load(self.graphfile)
      self.path = None
      self.srcpoint   = self.wTree.get_widget("combo-entry2").get_text()
      self.destpoint = self.wTree.get_widget("combo-entry3").get_text()

      
      self.edit_mode = False
      self.edge_started = False
      self.move_vertex = None
      self.current_vertex = None
      self.name_entry = self.wTree.get_widget("entry1")

      self.zoom_scale = 0
   
      dic = { "on_algo1_clicked" :           # find path
                 self.on_algo1,
              "on_button2_clicked":            # refresh image
                 self.on_refresh,
              "on_save_clicked" :           # save
                 self.on_save,
                
              "on_togglebutton1_clicked":  # edit mode
                 self.on_edit_mode,
                
              "on_checkbutton1_toggled":   # vertices
                 self.toggled_event,
              "on_checkbutton2_toggled":   # edege
                 self.toggled_event,
              "on_checkbutton3_toggled":   # label
                 self.toggled_event,
              "on_entry1_changed":         # label name changed
                 self.on_name_changed,
                
              "on_drawingarea1_expose_event" :  # redraw area
                 self.on_drawingarea1_expose_event,

              "on_drawingarea1_motion_notify_event":   # mouse move
                 self.on_drawingarea1_motion_notify_event,

              "on_drawingarea1_button_press_event" :   # mouse pushed down
                 self.on_drawingarea1_button_press_event,

              "on_drawingarea1_button_release_event":  # mouse release
                 self.on_drawingarea1_button_release_event,

              "on_algo2_clicked":  # algo -2
                 self.on_algo2 ,
              "on_asearch_clicked":   # the A* search
                 self.on_asearch  ,
              "on_help_clicked":   # help
                 self.on_help  ,
                 
              "on_zoomin_clicked" :
                 self.on_zoom,
              "on_zoomout_clicked" :
                 self.on_zoom,
              "on_actualsize_clicked" :
                 self.on_zoom,
                 
                 
              "on_exit":   # Quit
                 (gtk.mainquit)
             }
      self.wTree.signal_autoconnect(dic)   #3

      # create some graphics contexts to use for drawing
      self.vertex_brush = self.canvas.window.new_gc()
      self.vertex_brush_color = self.colormap.alloc_color("green")
      self.vertex_brush.set_foreground( self.vertex_brush_color )

      self.edge_brush = self.canvas.window.new_gc()
      self.edge_brush_color = self.colormap.alloc_color("blue")
      self.edge_brush.set_foreground( self.edge_brush_color )
      self.edge_brush.line_width = 5

      self.name_brush = self.canvas.window.new_gc()
      self.name_brush_color = self.colormap.alloc_color("red")
      self.name_brush.set_foreground( self.name_brush_color )

      self.path_brush = self.canvas.window.new_gc()
	  # line attributes
      self.path_brush_color = self.colormap.alloc_color("orange")
      self.path_brush.line_width = 10
      self.path_brush.line_style = gtk.gdk.LINE_ON_OFF_DASH
      self.path_brush.join_style = gtk.gdk.JOIN_ROUND
      self.path_brush.set_dashes( 0, [ 15, 10 ] )
      self.path_brush.set_foreground(self.path_brush_color)



   
   def on_drawingarea1_expose_event(self, widget, event):
            self.draw()

   def toggled_event(self,widget) :
            self.draw()


   #  reload the map image
   def on_refresh(self,widget):

         map2 = self.wTree.get_widget("combo-entry1").get_text()


#         self.edge_started = False
#         self.move_vertex = None
#         self.current_vertex = None

        
         if ( not ( map2 == self.map ) ) :
           self.map = map2
           self.mapfile = "maps/"+ self.map + ".png"   
           if self.mapfile is not None and os.path.exists(self.mapfile):
              self.basepixbuf = gtk.gdk.pixbuf_new_from_file(self.mapfile)
              self.currentpixbuf = self.basepixbuf
              self.w, self.h = ( self.currentpixbuf.get_width(), self.currentpixbuf.get_height() )
              self.canvas.set_size_request( self.w, self.h )

      
         self.graphfile = "graphs/"+self.map + ".graph"
         self.graph.load(self.graphfile)
         self.path = None
         self.edit_mode = False
         self.zoom_scale = 0
         
         self.draw()


   def  on_save(self,widget):

        filename = None
        if self.graphfile is not None:
            filename = self.graphfile
        else:
            filename = "graph.txt"

        if len(self.graph.vertices) > 0:
            print "save %s" % filename
            self.graph.save(filename)
            print "saving finished"
        else:
            print "no vertices.  not saving"

          
           
   # find the path
   def on_algo1(self,widget):
            self.path = self.find_path(1)
           
            if self.path is None:
                print "no path found"
            else:
                print "path found"

            self.draw()

   def on_algo2(self,widget):
            self.path = self.find_path(2)
           
            if self.path is None:
                print "no path found"
            else:
                print "path found"

            self.draw()


   def on_asearch(self,widget):
            self.path = self.find_path(3)
           
            if self.path is None:
                print "no path found"
            else:
                print "path found"

            self.draw()

            
   def find_path(self,algo) :
      self.srcpoint   = self.wTree.get_widget("combo-entry2").get_text()
      self.destpoint = self.wTree.get_widget("combo-entry3").get_text()

      #at first add the points to frequently-used list
      if self.srcpoint not in self.srclist :
         self.srclist.insert(0,self.srcpoint)
         if len(self.srclist) >5 :
              self.srclist.pop()
         self.wTree.get_widget("combo2").set_popdown_strings(self.srclist)
         
      if self.destpoint  not in self.destlist :
         self.destlist.insert(0,self.destpoint)
         if len(self.destlist) >5 :
             self.destlist.pop()
         self.wTree.get_widget("combo3").set_popdown_strings(self.destlist)
     
      p =self.find_path2(self.srcpoint,self.destpoint)
      return p
      
           
   def  find_path2(self, src, dest) :
      v1 = None
      v2 = None
      for v in self.graph.get_vertices():
            if v.name == src: v1 = v
            elif v.name == dest: v2 = v

      if v1 is None or v2 is None:
            #d = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,  flags=gtk.DIALOG_MODAL, buttons=gtk.BUTTONS_OK, message_format="bad vertex")
            #d.run()
            #d.destroy()
            return None
      else:
            # See search.py for heuristic algorithm
            problem = search.MapSearchProblem(v1, v2)
            p= search.astar_search( problem )
            return [ v for  v,e in p ]



   def on_zoom(self,widget) :

     widget_name = widget.get_name()
     if  widget_name == "zoomin" :
          self.zoom_scale = self.zoom_scale + 1
          print  " zoom in "
     elif  widget_name == "zoomout" :
          self.zoom_scale = self.zoom_scale - 1
          if self.zoom_scale <= int(-8) :    self.zoom_scale = int(-8)
          print  " zoom out "
     else :
          self.zoom_scale =0
          print  " actual size"
     

     if self.zoom_scale == 0 :
          self.currentpixbuf  = self.basepixbuf
          current_w , current_h =  ( self.w , self.h )          
     else :
          current_w , current_h =  ( self.zoom(self.w) , self.zoom(self.h) )
          self.currentpixbuf  = self.basepixbuf.scale_simple(current_w,current_h,gtk.gdk.INTERP_NEAREST)
          if  self.currentpixbuf is None :         
                  print "No more buffer!"
                  self.zoom_scale = 0
                  self.currentpixbuf = self.basepixbuf
                  current_w , current_h =  ( self.w , self.h )                            

     self.canvas.set_size_request( current_w, current_h )
     self.draw()


   def zoom(self,x) :
        if self.zoom_scale == 0 :
          return x

        rate1 = 10 + self.zoom_scale 
        rate2 = 10
        return int((int(x) * rate1) / rate2)

   def dezoom(self,x) :
        if self.zoom_scale == 0 :
          return x

        rate2 = 10 + self.zoom_scale 
        rate1 = 10
        return int((int(x) * rate1) / rate2)



   def draw(self) :

        current_w, current_h = ( self.currentpixbuf.get_width(), self.currentpixbuf.get_height() )
        self.currentpixbuf.render_to_drawable(self.canvas.window,self.gc,0, 0, 0, 0, current_w, current_h, 0, 0, 0) 

        self.vertice_cb   = self.wTree.get_widget("checkbutton1")
        self.edge_cb     = self.wTree.get_widget("checkbutton2")
        self.label_cb      = self.wTree.get_widget("checkbutton3")

        # draw a path, if it's there
        if self.path is not None:
                polyline = [ ( self.zoom(v.x)  , self.zoom(v.y) ) for v in self.path ]
                self.canvas.window.draw_lines( self.path_brush, polyline )
  
  
        # draw vertices
        if self.vertice_cb.get_active():
                  for v in self.graph.get_vertices():
                     x = self.zoom( int(v.x - self.graph.vertex_radius) )
                     y = self.zoom(int(v.y - self.graph.vertex_radius))
                     w = self.zoom(int(self.graph.vertex_radius * 2))
                     h = self.zoom(int(self.graph.vertex_radius * 2))
                     self.canvas.window.draw_arc( self.vertex_brush, gtk.TRUE, x, y, w, h,0, 360*64 )

        # draw the name...
        if self.label_cb.get_active():
                  for v in self.graph.get_vertices():
                     x = self.zoom(int(v.x - self.graph.vertex_radius) )
                     y = self.zoom(int(v.y - self.graph.vertex_radius))
                     w = self.zoom(int(self.graph.vertex_radius * 2))
                     h = self.zoom(int(self.graph.vertex_radius * 2))

                     if len(v.name) > 0:
                       layout = self.pangolayout 
                       layout.set_text( v.name )
                       lw,lh = layout.get_pixel_size()
                       lx = x - lw / 2
                       ly = y - lh / 2
                       self.canvas.window.draw_layout(self.name_brush, lx, ly, layout)

        # draw edges
        if self.edge_cb.get_active():
            for e in self.graph.get_edges():
                self.canvas.window.draw_line( self.edge_brush, self.zoom(e.v1.x) , self.zoom(e.v1.y ), self.zoom(e.v2.x) , self.zoom(e.v2.y) )




   def on_edit_mode(self,widget):
       self.edit_mode = (not self.edit_mode )
       print " change edit-mode "
       print self.edit_mode

   
   def on_name_changed(self,widget):
       if self.current_vertex is not None:
            self.current_vertex.name = self.name_entry.get_text()
            self.draw()




   # if want to store points into graph, the points from the event must be dezoom-ed !
   def on_drawingarea1_button_press_event(self,widget,event):
        if not self.edit_mode :
           print " not edit mode"
           return False

        self.cursor_x = int(event.x)
        self.cursor_y = int(event.y)

        ex = self.dezoom(event.x)
        ey = self.dezoom(event.y)

        if event.button == 1:   # left button click
            self.edge_started = False
            self.new_edge = None

            v = self.graph.cast_ray(ex, ey)
            if v is not None:
                # start moving a vertex
                self.move_vertex = v

                if self.current_vertex != v:
                    self.current_vertex = v
                    self.name_entry.set_text(v.name)
                    print "baby,i give you a name"
            else:
                # add a vertex
                self.graph.add_vertex( 1, ex, ey ,""  )
                print "add vertex"

        elif event.button == 2:  # middle click
                if self.edge_started:
                  v2 = self.graph.find_vertex( ex, ey )
                  if v2 is not None:
                    if self.new_edge.v1 != v2:
                        self.new_edge.v2 = v2
                        self.graph.edges.append( self.new_edge )
                    self.edge_started = False
                    self.new_edge = None
                else:
                  # start an edge
                  v1 = self.graph.find_vertex( ex, ey )
                  if v1 is not None:
                    self.edge_started = True
                    self.new_edge = graph.Edge( v1, v1 )

        elif event.button == 3:  # right click for vertex deletion
            self.edge_started = False
            self.new_edge = None

            # delete a vertex and all its edges
            v = self.graph.cast_ray( ex, ey )
            if v is not None:
                self.graph.remove_vertex(v.id)
                print "delete vertex"               

        self.draw()
        return True

   def on_drawingarea1_motion_notify_event(self,widget,event):
        if not self.edit_mode :
           return False
        self.cursor_x = int(event.x) 
        self.cursor_y = int(event.y)

        if event.state & gtk.gdk.BUTTON1_MASK:
            if self.move_vertex is not None:
                self.move_vertex.x = int(event.x)
                self.move_vertex.y = int(event.y)
        else:
            pass
        return True


   def on_drawingarea1_button_release_event(self,widget,event):
        self.move_vertex = None
        self.draw()



   # help
   def on_help(self,widget):   
            d = gtk.MessageDialog(type=gtk.MESSAGE_INFO, \
                    flags=gtk.DIALOG_MODAL, \
                    buttons=gtk.BUTTONS_OK, message_format= \
                    "1. FIND PATH  \
                       \nChoose the map ,Refresh to load image ,and choose from-to points  \
                       \nThen click any one of 3 algorithm button to find path  \
                       \nAlgo-1 : The recursive algorithm  \
                       \nAlgo-2 : The shortest path set algorithm  \
                       \nA* Search: The heuristic algorithm\n  \
                                    \
                       \n2. EDIT  \
                       \nDefault: is search mode  \
                       \nPress down Edit Mode button to enter edit mode.  \
                       \nadd vertex: left click somewhere   \
                       \nclear vertex: right click on vertex   \
                       \nmove vertex: left click on vertex, drag   \
                       \nadd edge: middle click first vertex, middle click second vertex   \
                       \nname vertex: left click on vertex, type name\n   \
                                  \
                       \n3. SAVE   \
                       \nAfter finishing editing, press Save button to save into *.graph file  \
                    "  )
            d.run()
            d.destroy()


   def  feed(self,server1) :


                   alias = {}
                   alias["coffee"] = "G814"
                   alias["elevator"]="G816"
                   alias["larry"] = "G818"
                   alias["bob"]  = "G822"
                   alias["water"] ="G825"
                   
                   
                   c = server1.handleMessage(0)        
                   if c:           
                          action = c.frame.getAction()
        
                          if (action == 'call_answered'): 
                                    c.sb_reply('Please enter voice command')
                                    print  "call answered"
        
                          elif (action == 'good_bye'): # Good bye means close off the conversation
                                    c.sb_goodbye('Good Bye')
                                    active = 0
            
                          elif (action == 'status') :
                                    room =  c.frame.getAttribute('room')
                                    prefix  =  c.frame.getAttribute('prefix')                                    
                                    source =    c.frame.getAttribute('source')
                                    if room != None :
                                         room = alias[room]
                                    if room== None :
                                        if prefix !=None and source != None :
                                               room = prefix + source

                                    print  c.frame.getText()
                                    
                                    if  room != None :
                                           print room

                                    if  self.graph.find_vertex_by_name(room) is None :
                                           c.sb_reply('I can not position where you are')                                                                              
                                    else  :
                                           self.srcpoint  = room
                                           c.sb_reply('I think you are at'+room ) 
                                           print "I think you are at %s" % room
                                           self.wTree.get_widget("combo-entry2").set_text(self.srcpoint)
                                   
                                    
                          elif (action == 'where') :
                                    room =  c.frame.getAttribute('room')
                                    prefix  =  c.frame.getAttribute('prefix')                                    
                                    destination =    c.frame.getAttribute('destination')
                                    digit  = c.frame.getAttribute('digit')
                                    digit2 =c.frame.getAttribute('digit2')
                                    
                                    if room != None :
                                         room = alias[room]
                                    if room== None :
                                        if prefix !=None and destination != None and digit !=None and digit2 !=None:
                                               room = prefix + digit+digit2  #destination

                                    print  c.frame.getText()
                                    
                                    if  room != None :
                                           print room

                                    if  self.graph.find_vertex_by_name(room) is None :
                                           c.sb_reply('I can not position where you want to go')                                                                              
                                    else  :
                                           self.destpoint  = room
                                           c.sb_reply('I think you want to go '+room ) 
                                           print "I think you want to go %s" % room
                                           if  self.srcpoint is not None  :
                                                self.path= self.find_path2(self.srcpoint,self.destpoint)
                                                self.draw()
                                                self.wTree.get_widget("combo-entry3").set_text(self.destpoint)
                                                if self.path !=None :
                                                        c.sb_reply('And I have shown your path from'+self.srcpoint+'to'+self.destpoint)
                                                else  :
                                                        c.sb_reply('But the path is not found')


                          elif (action == 'take') :
                                    room   = c.frame.getAttribute('room')
                                    prefix  = c.frame.getAttribute('prefix')
                                    source = c.frame.getAttribute('source')
                                    if  source != None and  prefix != None :
                                              source = prefix + source
                                    destination = c.frame.getAttribute('destination')
                                    if  destination != None and  prefix != None :
                                              destination = prefix + destination

                                    if  room != None :
                                              self.destpoint = alias[room]
                                    else  :
                                              self.destpoint = destination

                                    if source != None :
                                              self.srcpoint = source

                                    if  self.srcpoint is None  or self.destpoint is None :
                                          return 

                                    c.sb_reply('You want to go from'+self.srcpoint+'to'+self.destpoint)
                                    self.wTree.get_widget("combo-entry2").set_text(self.srcpoint)                                    
                                    self.wTree.get_widget("combo-entry3").set_text(self.destpoint)                                                                        
                                    self.path = self.find_path2(self.srcpoint,self.destpoint)                                     
                                    if self.path is None:        
                                            c.sb_reply('But the path is not found')
                                            print "no path found"
                                    else:
                                            c.sb_reply('And I have shown your path')
                                            print "path found"
                                            self.srcpoint = self.destpoint
                                            self.destpoint = None
                                            self.draw()



                          elif (action == 'load') :
                                    number =  c.frame.getAttribute('digit')
                                    prefix  =  c.frame.getAttribute('prefix')                                    
                                    if number !=None :
                                        map= number
                                        if prefix !=None :
                                           map  = map+ prefix

                                        c.sb_reply('You want to load map'+map)
                                        print "You want to load map %s" %map
                                        
                                        if ( not ( map == self.map ) ) :
                                                        self.map = map
                                                        self.mapfile = "maps/"+ self.map + ".png"   
                                                        if self.mapfile is not None and os.path.exists(self.mapfile):
                                                            self.basepixbuf = gtk.gdk.pixbuf_new_from_file(self.mapfile)
                                                            self.currentpixbuf = self.basepixbuf
                                                            self.w, self.h = ( self.currentpixbuf.get_width(), self.currentpixbuf.get_height() )
                                                            self.canvas.set_size_request( self.w, self.h )
       
                                        self.graphfile = "graphs/"+self.map + ".graph"
                                        self.graph.load(self.graphfile)
                                        self.path = None
                                        self.edit_mode = False
                                        self.zoom_scale = 0
                                        self.draw()
                                        self.wTree.get_widget("combo-entry1").set_text(self.map)

                                           
       
                          elif (action): # This means we really got some stuff
                                    mytext = c.frame.getText()        
                                    if mytext:
                                       c.sb_reply('I think you said '+ mytext)
                                    else:
                                       c.sb_reply('I dont know what you said')
                          else:
                                    c.sb_reply('I have no idea what is happening')  # This shouldn't happen

   
   

# Main program entrance

if __name__=="__main__":
    
        app = gui()
        server1 = galaxy.server.Server("soccf-smasrv01.ddns.comp.nus.edu.sg", 12887, "fanghui") 
        server1.connect()  # Actually connect to the Galaxy frame relay
        print " connected"        
        # Use the active variable to quit if we get a goodbye

        while (1) :
             while gtk.events_pending() :
                gtk.mainiteration()
             app.feed(server1)
