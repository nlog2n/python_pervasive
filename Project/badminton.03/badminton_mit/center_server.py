#!/usr/bin/env  python2.3

import sys
import socket
import random
import time

# create the server socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

port = int(sys.argv[1])

# allow the socket to be re-used immediately after a close
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind( ("0.0.0.0", port) )
# start the server socket
s.listen(5)

print "waiting for new connection on port %d" % port

i = 0

(client, address) = s.accept()
print "accepted connection from %s:%d\n" % (address[0], address[1])




while 1:
      location = random.choice(["1\n","2\n","3\n","4\n","5\n","6\n","7\n","8\n","9\n","-1\n","-2\n","-3\n","-4\n","-5\n","-6\n","-7\n","-8\n","-9\n"])
      try: 
       client.send(location)     
      except socket.error :
         print "send error"
         client.close()
         break
      print location
      time.sleep(3)
  
