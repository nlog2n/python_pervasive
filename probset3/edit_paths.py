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

VERTEX_RADIUS = 5

docstring= """ add vertex: \tleft click somewhere
 clear vertex:\tright click on vertex
 move vertex: \tleft click on vertex, drag
 add edge: \tmiddle click first vertex, middle click second vertex
 name vertex: \tleft click on vertex, type name
"""

class Vertex:
    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
        self.id = -1
        self.name = ""

class Edge:
    def __init__(self, v1, v2):
        self.v1 = v1
        self.v2 = v2

class MapMarker:
    def __init__(self):
	self.canvas = None
	self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	self.window.set_name ("Map Marker")
	self.window.set_title ("Map Marker")

	vbox = gtk.VBox(gtk.FALSE, 0)
	self.window.add(vbox)
	vbox.show()

	self.window.connect("destroy", gtk.mainquit)

        # Instructions
        tv = gtk.TextView()
        tv.set_editable(gtk.FALSE)
        buf = tv.get_buffer()
        buf.set_text(docstring)
        tv.show()
        tv.unset_flags(gtk.CAN_FOCUS)
        vbox.pack_start(tv, gtk.FALSE, gtk.FALSE, 0)
        
	# Create the drawing area
	# Create the drawing area
        self.canvas_sw = gtk.ScrolledWindow()
        self.canvas_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	self.canvas = gtk.DrawingArea()
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

        # for the labeling
        hbox = gtk.HBox(gtk.FALSE, 0)
        vbox.pack_start(hbox, gtk.FALSE, gtk.FALSE, 0)
        label = gtk.Label("name")
        self.name_entry = gtk.Entry()
        hbox.pack_start(label, gtk.FALSE, gtk.FALSE, 0)
        hbox.pack_start(self.name_entry, gtk.TRUE, gtk.TRUE, 0)
        label.show()
        self.name_entry.show()
        self.name_entry.connect("changed", self.name_entry_changed_event)
        hbox.show()

	# .. And some buttons
	quit_button = gtk.Button("_Quit")
	save_button = gtk.Button("_Save")

	hbox = gtk.HBox(gtk.FALSE, 0)
	vbox.pack_start(hbox, gtk.FALSE, gtk.FALSE, 0)
	hbox.pack_start(save_button, gtk.TRUE, gtk.TRUE, 0)
	hbox.pack_start(quit_button, gtk.TRUE, gtk.TRUE, 0)
	hbox.show()

	save_button.connect("clicked", self.save_event)
	quit_button.connect_object("clicked", \
		lambda w: w.destroy(), self.window)

	save_button.show()
	quit_button.show()

        self.vertices = []
        self.edges = []
        self.edge_started = False
        self.move_vertex = None
        self.current_vertex = None

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



    def load_graph(self, filename):
        try:
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
                    new_vertex = Vertex(x, y)
                    new_vertex.id = id
                    new_vertex.name = name
                    self.vertices.append(new_vertex)
                elif s[:4] == "edge":
                    junk, vid1, vid2 = s.split(',')
                    v1 = None
                    v2 = None
                    for v in self.vertices:
                        if v.id == vid1: v1 = v
                        elif v.id == vid2: v2 = v
                    if v1 is not None and v2 is not None:
                        self.edges.append( Edge( v1, v2 ) )
                    else:
                        print "bad edge (%s, %s)" % (vid1, vid2)

            f.close()
        except IOError, e:
            print e

    def save_graph(self, filename):
        try:
            f = file(filename, "w")
            i = 0
            for v in self.vertices:
                v.id = i
                f.write("vertex,%s,%s,%s,%s\n" % (v.id, v.x, v.y, v.name))
                i = i + 1

            for e in self.edges:
                f.write("edge,%s,%s\n" % (e.v1.id, e.v2.id))
            f.close()
        except IOError, e:
            print e

    def save_event(self, widget):
        filename = None
        if self.graphfile is not None:
            filename = self.graphfile
        else:
            filename = "graph.txt"

        if len(self.vertices) > 0:
            print "save %s" % filename
            self.save_graph(filename)
        else:
            print "no vertices.  not saving"

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

    def name_entry_changed_event(self, widget):
#        v = self.find_vertex(self.cursor_x, self.cursor_y)
        if self.current_vertex is not None:
            self.current_vertex.name = self.name_entry.get_text()
            self.draw()

    def draw(self):
	cw, ch = ( self.original.get_width(), self.original.get_height() )
	self.buffer.draw_drawable(self.canvas.get_style().fg_gc[gtk.STATE_NORMAL],
				    self.base_pixmap, 0,0,0,0,cw,ch) 

        # draw edges
        for e in self.edges:
            self.buffer.draw_line( self.edge_brush, e.v1.x, e.v1.y, \
                    e.v2.x, e.v2.y )

        # draw new edge
        if self.edge_started:
            e = self.new_edge
            self.buffer.draw_line( self.edge_brush, e.v1.x, e.v1.y, \
                    self.cursor_x, self.cursor_y )

        # draw vertices
        for v in self.vertices:
            x = int(v.x - VERTEX_RADIUS)
            y = int(v.y - VERTEX_RADIUS)
            w = int(VERTEX_RADIUS * 2)
            h = int(VERTEX_RADIUS * 2)

            # draw the vertex
            self.buffer.draw_arc( self.vertex_brush, gtk.TRUE, x, y, w, h, \
                   0, 360*64 )

            # draw the name...
            if len(v.name) > 0:
                layout = pango.Layout(self.canvas.get_pango_context())
                layout.set_text( v.name )
		lw,lh = layout.get_pixel_size()
		lx = x - lw / 2
		ly = y - lh / 2
		self.buffer.draw_layout(self.name_brush, lx, ly, layout)

            
        self.canvas.queue_draw_area(0,0,cw,ch)

    def find_vertex(self, x, y):
        if len(self.vertices) == 0: return None
        closest = self.vertices[0]
        closest_dist = (closest.x - x)*(closest.x - x) + \
                (closest.y - y)*(closest.y - y)

        for v in self.vertices:
            dist = (v.x - x)*(v.x-x) + (v.y-y)*(v.y-y)
            if dist < closest_dist:
                closest = v
                closest_dist = dist
        return closest

    def cast_ray(self, x, y):
        min_dist = VERTEX_RADIUS * VERTEX_RADIUS

        for v in self.vertices:
            dist = (v.x - x)*(v.x-x) + (v.y-y)*(v.y-y)
            if dist < min_dist: return v

        return None

    def button_press_event(self, widget, event):
	# event.x, event.y
	# event.button
	w, h = ( self.original.get_width(), self.original.get_height() )
        self.cursor_x = int(event.x)
        self.cursor_y = int(event.y)

	if event.button == 1:
            self.edge_started = False
            self.new_edge = None

            v = self.cast_ray(event.x, event.y)
            if v is not None:
                # start moving a vertex
                self.move_vertex = v

                if self.current_vertex != v:
                    self.current_vertex = v
                    self.name_entry.set_text(v.name)
            else:
                # add a vertex
                self.vertices.append( Vertex( event.x, event.y ) )
	elif event.button == 2:
            if self.edge_started:
                v2 = self.find_vertex( event.x, event.y )
                if v2 is not None:
                    if self.new_edge.v1 != v2:
                        self.new_edge.v2 = v2
                        self.edges.append( self.new_edge )
                    self.edge_started = False
                    self.new_edge = None
            else:
                # start an edge
                v1 = self.find_vertex( event.x, event.y )
                if v1 is not None:
                    self.edge_started = True
                    self.new_edge = Edge( v1, v1 )
	elif event.button == 3:
            self.edge_started = False
            self.new_edge = None

            # delete a vertex and all its edges
            v = self.cast_ray( event.x, event.y )
            if v is not None:
                self.vertices.remove(v)
                for e in self.edges[:]:
                    if e.v1 == v or e.v2 == v:
                        self.edges.remove(e)

        self.draw()
	return gtk.TRUE

    def motion_notify_event(self, widget, event):
        self.cursor_x = int(event.x)
        self.cursor_y = int(event.y)

        if event.state & gtk.gdk.BUTTON1_MASK:
            if self.move_vertex is not None:
                self.move_vertex.x = int(event.x)
                self.move_vertex.y = int(event.y)
        else:
            pass
#        if self.edge_started:
#            self.new_edge.v2 = self.find_vertex( event.x, event.y )

#        self.draw()
	return gtk.TRUE

    def button_release_event(self, widget, event):
        self.move_vertex = None

    def run(self, mapfile, graphfile = None):
	print "running"
#        self.load_file( filename )
	self.window.show()
        self.graphfile = graphfile
        if self.graphfile is not None and os.path.exists(self.graphfile):
            self.load_graph( graphfile )

        self.load_image( mapfile )
        self.draw()

	gtk.main()


if __name__ == "__main__":
    if len(sys.argv) < 2:
	print "usage: edit_paths.py underlay_image [graphfile]"
	sys.exit(2)

    mapfile = sys.argv[1]
    graphfile = None

    if len(sys.argv) > 2:
        graphfile = sys.argv[2]

    mm = MapMarker()
    mm.run(mapfile, graphfile)
