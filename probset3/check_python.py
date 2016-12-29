#!/usr/bin/env python 

import sys 
try: 
   import pygtk 
   pygtk.require("2.0") 
except: 
   pass 
try: 
   import gtk 
   import gtk.glade 
except: 
   print "GTK is not installed" 
   sys.exit(1) 