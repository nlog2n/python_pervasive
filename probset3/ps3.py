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

pygtk.require("2.0")
import gtk
import gtk.glade
import gtk.gdk
import gobject
import math
import pango
import string


import graph
import search  # A* search algo


VERTEX_RADIUS = 5

def weight(v1, v2):
    return math.sqrt((v1.x-v2.x)*(v1.x-v2.x) + (v1.y-v2.y)*(v1.y-v2.y))


class MapSearchProblem(search.SearchProblem):
    """a class of search problem that uses straight line distance from vertex
    to goal as the heuristic
    """
    def __init__(self, start_vertex, goal_vertex):
        self.initial_state = start_vertex
        self.goal_vertex = goal_vertex

    def successors(self, vertex):
        return [ ( edge, edge.v2 ) for edge in vertex.out_edges ]
    
    def is_goal(self, vertex):
        return vertex == self.goal_vertex

    def step_cost(self, v1, action, v2):
        return math.sqrt((v1.x-v2.x)*(v1.x-v2.x) + (v1.y-v2.y)*(v1.y-v2.y))

    def estimated_cost_from( self, vertex ):
        v1 = vertex
        v2 = self.goal_vertex
        return math.sqrt((v1.x-v2.x)*(v1.x-v2.x) + (v1.y-v2.y)*(v1.y-v2.y))



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
      self.pixbuf = None
      self.mapfile = "maps/"+ self.map + ".png"   
      if self.mapfile is not None and os.path.exists(self.mapfile):
            self.pixbuf = gtk.gdk.pixbuf_new_from_file(self.mapfile)
            self.w, self.h = ( self.pixbuf.get_width(), self.pixbuf.get_height() )
            self.canvas.set_size_request( self.w, self.h )
            self.pixbuf.render_to_drawable(self.canvas.window,self.gc,0, 0, 0, 0, self.w, self.h, 0, 0, 0)


      #save frequently-used list
      self.srclist = []
      self.destlist= []

      self.load_graph()
      self.edit_mode = False
      self.edge_started = False
      self.move_vertex = None
      self.current_vertex = None
      self.name_entry = self.wTree.get_widget("entry1")

      self.zoom_scale = 0
      self.zoom_in    = True
   
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
                 self.on_zoomin,
              "on_zoomout_clicked" :
                 self.on_zoomout,
              "on_actualsize_clicked":
                 self.on_actualsize,
                 
              "on_exit":   # Quit
                 (gtk.main_quit)
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

#         self.edit_mode = False
#         self.edge_started = False
#         self.move_vertex = None
#         self.current_vertex = None

         
         if ( not ( map2 == self.map ) ) :

           self.load_graph()
           self.map = map2
           self.mapfile = "maps/"+ self.map + ".png"   
           #if self.pixbuf not None
             # free
           if self.mapfile is not None and os.path.exists(self.mapfile):
              self.pixbuf = gtk.gdk.pixbuf_new_from_file(self.mapfile)
              self.w, self.h = ( self.pixbuf.get_width(), self.pixbuf.get_height() )
              self.canvas.set_size_request( self.w, self.h )
#              self.pixbuf.render_to_drawable(self.canvas.window,self.gc,0, 0, 0, 0, self.w, self.h, 0, 0, 0)

         else :
              self.load_graph()

         self.draw()

          
           
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
      src  = self.wTree.get_widget("combo-entry2").get_text()
      dest = self.wTree.get_widget("combo-entry3").get_text()

      #at first add the points to frequently-used list
      if src not in self.srclist :
         self.srclist.insert(0,src)
         if len(self.srclist) >5 :
              self.srclist.pop()
         self.wTree.get_widget("combo2").set_popdown_strings(self.srclist)
      if dest not in self.destlist :
         self.destlist.insert(0,dest)
         if len(self.destlist) >5 :
             self.destlist.pop()
         self.wTree.get_widget("combo3").set_popdown_strings(self.destlist)
     
     
      v1 = None
      v2 = None
      for v in self.graph.get_vertices():
            if v.name == src: v1 = v
            elif v.name == dest: v2 = v

      if v1 is None or v2 is None:
            d = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, \
                    flags=gtk.DIALOG_MODAL, \
                    buttons=gtk.BUTTONS_OK, message_format="bad vertex")
            d.run()
            d.destroy()
            return None
      else:
            if algo == 1 :
                # See search.py for heuristic algorithm
                problem = MapSearchProblem(v1, v2)
                p= search.astar_search( problem )
                return [ v for  v,e in p ]

            elif algo ==2  :
                # See graph.py for detail about recursive algorithm
                return self.graph.find_path(v1,v2)

            elif algo ==3  :
                #return self.graph.find_path2(v1,v2)            
                # See graph.py for detail about shortest path set algorithm
                problem = MapSearchProblem(v1, v2)
                p= search.astar_search( problem )
                return [ v for  v,e in p ]

            else  :
                return None
           
   def on_zoomin(self,widget) :
      self.zoom_scale = self.zoom_scale + 1
      self.draw()

   def on_zoomout(self,widget) :
      self.zoom_scale = self.zoom_scale - 1
      if self.zoom_scale <= int(-8) :
         self.zoom_scale = int(-8)
      self.draw()

   def on_actualsize(self,widget) :
      self.zoom_scale =0
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

        
        current_w, current_h = ( self.w, self.h)

        if self.zoom_scale != 0 :
          current_w , current_h =  ( self.zoom(current_w) , self.zoom(current_h) )
          tmp_pixbuf = self.pixbuf.scale_simple(current_w,current_h,gtk.gdk.INTERP_NEAREST)
          if tmp_pixbuf is None :
             print "No more buffer!"
          self.canvas.set_size_request( current_w, current_h )
        else :
          tmp_pixbuf = self.pixbuf

        tmp_pixbuf.render_to_drawable(self.canvas.window,self.gc,0, 0, 0, 0, current_w, current_h, 0, 0, 0) 

        self.vertice_cb = self.wTree.get_widget("checkbutton1")
        self.edge_cb    = self.wTree.get_widget("checkbutton2")
        self.label_cb   = self.wTree.get_widget("checkbutton3")

        # draw a path, if it's there
        if self.path is not None:
                polyline = [ ( self.zoom(v.x)  , self.zoom(v.y) ) for v in self.path ]
                self.canvas.window.draw_lines( self.path_brush, polyline )
  
  
        # draw vertices
        if self.vertice_cb.get_active():
                  for v in self.graph.get_vertices():
                     x = self.zoom( int(v.x - VERTEX_RADIUS) )
                     y = self.zoom(int(v.y - VERTEX_RADIUS))
                     w = self.zoom(int(VERTEX_RADIUS * 2))
                     h = self.zoom(int(VERTEX_RADIUS * 2))
                     self.canvas.window.draw_arc( self.vertex_brush, gtk.TRUE, x, y, w, h,0, 360*64 )

        # draw the name...
        if self.label_cb.get_active():
                  for v in self.graph.get_vertices():
                     x = self.zoom(int(v.x - VERTEX_RADIUS) )
                     y = self.zoom(int(v.y - VERTEX_RADIUS))
                     w = self.zoom(int(VERTEX_RADIUS * 2))
                     h = self.zoom(int(VERTEX_RADIUS * 2))

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





   def load_graph(self):

        map = self.wTree.get_widget("combo-entry1").get_text()
        self.graphfile = "graphs/"+map + ".graph"
        self.path = None
        if self.graphfile is not None and  os.path.exists(self.graphfile):
          try:
             self.graph = graph.Graph()
             self.graph.clear()

             f = file(self.graphfile)

             while True:
                s = f.readline()
                if len(s) == 0: break
                s = s.strip()
                if s[:6] == "vertex":
                    items = s.split(',')
                    id = items[1]
                    x = items[2]
                    y = items[3]
                    name = ""
                    if len(items) > 4:
                        name = items[4]
                    new_vertex = self.graph.add_vertex(id,x,y,name)

                elif s[:4] == "edge":
                    junk, vid1, vid2 = s.split(',')
                    try:
                        v1 = self.graph.get_vertex(vid1)
                        v2 = self.graph.get_vertex(vid2)
                        self.graph.add_edge( v1, v2, weight( v1, v2 ) )
                        self.graph.add_edge( v2, v1, weight( v2, v1 ) )
                    except:
                        print "bad edge (%s, %s)" % (vid1, vid2)

             f.close()
          except IOError, e:
            print e


   def  on_save(self,widget):

        filename = None
        if self.graphfile is not None:
            filename = self.graphfile
        else:
            filename = "graph.txt"

        if len(self.graph.vertices) > 0:
            print "save %s" % filename
            self.save_graph(filename)
            print "saving finished"
        else:
            print "no vertices.  not saving"


   def save_graph(self, filename):

        try:
            f = file(filename, "w")
            i = 0
            for v in self.graph.vertices.values():
                v.id = i
                f.write("vertex,%s,%s,%s,%s\n" % (v.id, v.x, v.y, v.name))
                i = i + 1

            for e in self.graph.edges:
                f.write("edge,%s,%s\n" % (e.v1.id, e.v2.id))
            f.close()
        except IOError, e:
            print e



   def on_edit_mode(self,widget):
       self.edit_mode = (not self.edit_mode )
       print " change edit-mode "
       print self.edit_mode

   
   def on_name_changed(self,widget):
       if self.current_vertex is not None:
            self.current_vertex.name = self.name_entry.get_text()
            self.draw()


   def cast_ray(self, x, y):
        min_dist = VERTEX_RADIUS * VERTEX_RADIUS

        for v in self.graph.vertices.values():
            dist = (v.x - x)*(v.x-x) + (v.y-y)*(v.y-y)
            if dist < min_dist: return v

        return None


   # if want to store points into graph, the points from the event must be dezoom-ed !
   
   def on_drawingarea1_button_press_event(self,widget,event):
        if not self.edit_mode :
           print " not edit mode"
           return False

        self.cursor_x = int(event.x)
        self.cursor_y = int(event.y)

        if event.button == 1:   # left button click
            self.edge_started = False
            self.new_edge = None

            v = self.cast_ray(self.dezoom(event.x), self.dezoom(event.y))
            if v is not None:
                # start moving a vertex
                self.move_vertex = v

                if self.current_vertex != v:
                    self.current_vertex = v
                    self.name_entry.set_text(v.name)
                    print "baby,i give you a name"
            else:
                # add a vertex
                self.graph.add_vertex( 1, self.dezoom(event.x), self.dezoom(event.y) ,""  )
                print "add vertex"

        elif event.button == 2:  # middle click
                if self.edge_started:
                  v2 = self.graph.find_vertex( self.dezoom(event.x), self.dezoom(event.y) )
                  if v2 is not None:
                    if self.new_edge.v1 != v2:
                        self.new_edge.v2 = v2
                        self.graph.edges.append( self.new_edge )
                    self.edge_started = False
                    self.new_edge = None
                else:
                  # start an edge
                  v1 = self.graph.find_vertex( self.dezoom(event.x), self.dezoom(event.y) )
                  if v1 is not None:
                    self.edge_started = True
                    self.new_edge = graph.Edge( v1, v1 )

        elif event.button == 3:  # right click for vertex deletion
            self.edge_started = False
            self.new_edge = None

            # delete a vertex and all its edges
            v = self.cast_ray( self.dezoom(event.x), self.dezoom(event.y) )
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
#        if self.edge_started:
#            self.new_edge.v2 = self.find_vertex( self.dezoom(event.x), self.dezoom(event.y) )

#        self.draw()
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




# Main program entrance

app=gui()
gtk.main()
