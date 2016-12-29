#!/usr/bin/env python
#
"""
"""

import os
import sys
import gtk
import gobject
import pango
import math

import graph
import search

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


class PathFinder:
    def __init__(self):
	self.canvas = None
	self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	self.window.set_name ("Map Marker")
	self.window.set_title ("Map Marker")

	vbox = gtk.VBox(gtk.FALSE, 0)
	self.window.add(vbox)

	self.window.connect("destroy", gtk.mainquit)

        # and a text view
        tv = gtk.TextView()
        tv.set_editable(gtk.FALSE)
        buf = tv.get_buffer()
        buf.set_text("Usage:  pick two rooms.  Type them in.  " + \
                "Click \"Find Path\"\n\n")
        tv.show()
        tv.unset_flags(gtk.CAN_FOCUS)
        vbox.pack_start(tv, gtk.FALSE, gtk.FALSE, 0)
        
        # some checkboxes
        hbox = gtk.HBox(gtk.TRUE, 0)
        self.show_vertices_cb = gtk.CheckButton("show vertices")
        self.show_vertices_cb.show()
        self.show_vertices_cb.connect("toggled", lambda w: self.draw())
        hbox.pack_start(self.show_vertices_cb, gtk.FALSE, gtk.FALSE, 0)
        self.show_edges_cb = gtk.CheckButton("show edges")
        self.show_edges_cb.show()
        self.show_edges_cb.connect("toggled", lambda w: self.draw())
        hbox.pack_start(self.show_edges_cb, gtk.FALSE, gtk.FALSE, 0)
        self.show_labels_cb = gtk.CheckButton("show labels")
        self.show_labels_cb.show()
        self.show_labels_cb.connect("toggled", lambda w: self.draw())
        hbox.pack_start(self.show_labels_cb, gtk.FALSE, gtk.FALSE, 0)
        hbox.show()
        vbox.pack_start(hbox, gtk.FALSE, gtk.FALSE, 0)

	# Create the drawing area
        self.canvas_sw = gtk.ScrolledWindow()
        self.canvas_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	self.canvas = gtk.DrawingArea()
#	self.canvas.set_size_request(200, 200)
#	vbox.pack_start(self.canvas, gtk.TRUE, gtk.TRUE, 0)
	vbox.pack_start(self.canvas_sw, gtk.TRUE, gtk.TRUE, 0)
        self.canvas_sw.add_with_viewport(self.canvas)
        self.canvas_sw.show()

	self.canvas.show()

	# Signals used to handle backing pixmap
	self.canvas.connect("expose_event",    self.expose_event)
	self.canvas.connect("configure_event", self.configure_event)

	# Event signals
	self.canvas.connect("motion_notify_event",  self.motion_notify_event)
	self.canvas.connect("button_press_event",   self.button_press_event)
	self.canvas.connect("button_release_event", self.button_release_event)

	self.canvas.set_events(gtk.gdk.EXPOSURE_MASK
				| gtk.gdk.LEAVE_NOTIFY_MASK
				| gtk.gdk.BUTTON_PRESS_MASK
				| gtk.gdk.BUTTON_RELEASE_MASK
				| gtk.gdk.POINTER_MOTION_MASK )

        # the "from" and "to" labels and text entries
        hbox = gtk.HBox(gtk.FALSE, 0)
        vbox.pack_start(hbox, gtk.FALSE, gtk.FALSE, 0)
        label = gtk.Label("from:")
        self.from_entry = gtk.Entry()
        hbox.pack_start(label, gtk.FALSE, gtk.FALSE, 0)
        hbox.pack_start(self.from_entry, gtk.TRUE, gtk.TRUE, 0)
        label.show()
        self.from_entry.show()

        label = gtk.Label("to:")
        self.to_entry = gtk.Entry()
        hbox.pack_start(label, gtk.FALSE, gtk.FALSE, 0)
        hbox.pack_start(self.to_entry, gtk.TRUE, gtk.TRUE, 0)
        label.show()
        self.to_entry.show()
        hbox.show()

	# .. And some buttons
	quit_button = gtk.Button("_Quit")
	find_path_button = gtk.Button("_Find Path")
	revert_button = gtk.Button("_Revert")

	hbox = gtk.HBox(gtk.FALSE, 0)
	vbox.pack_start(hbox, gtk.FALSE, gtk.FALSE, 0)
	hbox.pack_start(find_path_button, gtk.TRUE, gtk.TRUE, 0)
	hbox.pack_start(revert_button, gtk.TRUE, gtk.TRUE, 0)
	hbox.pack_start(quit_button, gtk.TRUE, gtk.TRUE, 0)
	hbox.show()

	find_path_button.connect("clicked", self.find_path_button_clicked)
	revert_button.connect("clicked", self.revert_event)
	quit_button.connect_object("clicked", \
		lambda w: w.destroy(), self.window)

	find_path_button.show()
#	revert_button.show()
	quit_button.show()

	vbox.show()

        self.graph = None

        self.path = None


    def load_image(self, filename):
	# load the image
	self.original = gtk.gdk.pixbuf_new_from_file(filename)

	w, h = ( self.original.get_width(), self.original.get_height() )
#	self.canvas.set_size_request( w, h )
	self.canvas_sw.set_size_request( w, h )

	# dup it
	self.buffer = gtk.gdk.Pixmap(self.canvas.window, w, h)
	self.base_pixmap = gtk.gdk.Pixmap(self.canvas.window, w, h)
	self.original.render_to_drawable( self.buffer, \
		self.canvas.get_style().fg_gc[gtk.STATE_NORMAL], \
		0, 0, 0, 0, w, h, 0, 0, 0)
	self.original.render_to_drawable( self.base_pixmap, \
		self.canvas.get_style().fg_gc[gtk.STATE_NORMAL], \
		0, 0, 0, 0, w, h, 0, 0, 0)

	self.colormap = self.canvas.get_colormap()

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

    def load_graph(self, filename):
        try:
            self.graph = graph.Graph()

            f = file(filename)

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
                    new_vertex = self.graph.add_vertex(id)

                    # some hack
                    new_vertex.x = int(x)
                    new_vertex.y = int(y)
                    new_vertex.name = name
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

    def find_path_button_clicked(self, widget):
        vid1 = self.from_entry.get_text()
        vid2 = self.to_entry.get_text()
        v1 = None
        v2 = None
        for v in self.graph.get_vertices():
            if v.name == vid1: v1 = v
            elif v.name == vid2: v2 = v

        if v1 is None or v2 is None:
            d = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, \
                    flags=gtk.DIALOG_MODAL, \
                    buttons=gtk.BUTTONS_OK, message_format="bad vertex")
            d.run()
            d.destroy()
        else:
            problem = MapSearchProblem(v1, v2)
            self.path = search.astar_search( problem )
            if self.path is None:
                print "no path found"
            else:
                print "path found"

            self.draw()

    def revert_event(self, widget):
        pass

    # Create a new backing pixmap of the appropriate size
    def configure_event(self, widget, event):
	return gtk.TRUE

    # Redraw the screen from the backing pixmap
    def expose_event(self, widget, event):
	x, y, width, height = widget.get_allocation()
	widget.window.draw_drawable(widget.get_style().fg_gc[gtk.STATE_NORMAL],
				    self.buffer, x, y, x, y, width, \
					    height)
	return gtk.FALSE

    def draw(self):
	cw, ch = ( self.original.get_width(), self.original.get_height() )
	self.buffer.draw_drawable(self.canvas.get_style().fg_gc[gtk.STATE_NORMAL],
				    self.base_pixmap, 0,0,0,0,cw,ch) 

        # draw edges
        if self.show_edges_cb.get_active():
            for e in self.graph.get_edges():
                self.buffer.draw_line( self.edge_brush, e.v1.x, e.v1.y, \
                        e.v2.x, e.v2.y )

        # draw vertices
        for v in self.graph.get_vertices():
            x = int(v.x - VERTEX_RADIUS)
            y = int(v.y - VERTEX_RADIUS)
            w = int(VERTEX_RADIUS * 2)
            h = int(VERTEX_RADIUS * 2)

#            # draw the vertex
            if self.show_vertices_cb.get_active():
                self.buffer.draw_arc( self.vertex_brush, gtk.TRUE, x, y, w, h, \
                       0, 360*64 )

            # draw the name...
            if self.show_labels_cb.get_active():
                if len(v.name) > 0:
                    layout = pango.Layout(self.canvas.get_pango_context())
                    layout.set_text( v.name )
                    lw,lh = layout.get_pixel_size()
                    lx = x - lw / 2
                    ly = y - lh / 2
                    self.buffer.draw_layout(self.name_brush, lx, ly, layout)

        # draw a path, if it's there
        if self.path is not None:
            polyline = [ (v.x, v.y) for v, e in self.path ]
	    self.buffer.draw_lines( self.path_brush, polyline )
            
        self.canvas.queue_draw_area(0,0,cw,ch)

    def button_press_event(self, widget, event):
        pass
	# event.x, event.y
	# event.button
	return gtk.TRUE

    def motion_notify_event(self, widget, event):
#        if self.edge_started:
#            self.new_edge.v2 = self.find_vertex( event.x, event.y )
	return gtk.TRUE

    def button_release_event(self, widget, event):
        return gtk.TRUE

    def run(self, mapfile, graphfile = None):
	print "running"
	self.window.show()
        self.graphfile = graphfile
        if self.graphfile is not None and os.path.exists(self.graphfile):
            self.load_graph( graphfile )

        self.load_image( mapfile )
        self.draw()

	gtk.main()

def run_path_finder(mapfile, graphfile):
    pf = PathFinder()
    pf.run(mapfile, graphfile)

if __name__ == "__main__":
    if len(sys.argv) < 2:
	print "usage: path_finder.py mapfile [graphfile]"
	sys.exit(2)

    mapfile = sys.argv[1]
    graphfile = None

    if len(sys.argv) > 2:
        graphfile = sys.argv[2]

    run_path_finder(mapfile, graphfile)
