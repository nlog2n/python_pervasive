import sys
import socket


if len(sys.argv) < 3: 
    print "usage: socketclient <address> <port>"
    sys.exit(2)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

s.connect( (sys.argv[1], int(sys.argv[2]) ) )

print "connected.  type stuff."

x = 1
while x:
    data = sys.stdin.readline()
    if len(data) == 0:
        print "closing connection with server"
        break

    s.send(data)
