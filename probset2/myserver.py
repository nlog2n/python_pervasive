import sys
import socket

if len(sys.argv) < 2:
    print "usage: socketserver <port>"
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
(client, address) = s.accept()
print "accepted connection from %s:%d" % (address[0], address[1])

x=1
while x:
    data = client.recv(1024)

    if len(data) == 0:
        print "connection with %s closed." % address[0]
        break

    sys.stdout.write(data)

client.close()
