#!/usr/bin/env  python2.3
#
"""
Speechbuilder interface, Fang Hui fh2008@hotmail.com	
"""

import os
import sys
import pygtk

#pygtk.require("2.0")
import gtk

import gtk.gdk
import gobject
import math
import string

import galaxy.server

######### Refer to methods in ####
#/usr/lib/python2.3/site-packages/galaxy/
#parser.py, server.py, frame.py
# methods in frame
# getKind(), Frame.CLAUSE,TOPIC,PREDICATE,UNKNOWN,
# getProperty(name)
# getAction()
#getText()
#getAttribute(name)


class SpeechHandler:

  
   def __init__(self):

      # FRAME RELAY = 12887 is used by backend(this) script  
      # ( galaudio use Oxogen port, see portmap )#
      # user name  = fanghui   same with  "relay:fanghui" at server side
      # server name = soccf-smasrv01.ddns.comp.nus.edu.sg

      self.server = galaxy.server.Server("soccf-smasrv01.ddns.comp.nus.edu.sg", 12887, "fanghui") 
      self.server.connect()  # Actually connect to the Galaxy frame relay
      if self.server.connected :    print " connected"        
      else : print " server not connected"

