import sys
import socket
import random
import time


if len(sys.argv) < 3: 
    print "usage: socketclient <address> <port>"
    sys.exit(2)

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

host = str(sys.argv[1])
port = int(sys.argv[2])

s.connect( ( host,port) ) 

print "connected. "

x = 1
while x:
    location = random.choice(["335,260\n","0,0\n","670,520\n","670,0\n","0,520\n"])
    try:
       s.sendto(location, (host,port))
    except socket.error :
       print "socket send error"
    time.sleep(3)
   
