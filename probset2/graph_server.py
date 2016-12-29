#! /opt/sfw/bin/python

# 6.894 problem set 2 - to find the path between 2 points in graph
# server side program
# Fang Hui 2004.9.29

import sys
import socket

if len(sys.argv) < 2:
    print "usage: graph_server <port>"
    sys.exit(2)

# create the server socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = int(sys.argv[1])
# allow the socket to be re-used immediately after a close
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind( ("0.0.0.0", port) )
# start the server socket
s.listen(5)

print "waiting for new connection on port %d" % port
while 1 :
  (client, address) = s.accept()
  print "accepted connection from %s:%d\n" % (address[0], address[1])

  while 1:
      data = client.recv(1024)
      if len(data) == 0 :
          print "\n\nconnection with %s closed." % address[0]
          break
      #print "path received:%s\n" % data    
      sys.stdout.write(data)
  
  client.close()