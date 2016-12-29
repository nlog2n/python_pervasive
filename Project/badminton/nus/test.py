from socket import *

host = "18.187.7.31"
port = 16001
addr = (host,port)

sock=socket(AF_INET,SOCK_DGRAM)
msg="Hello from the client!"

for i in range(10):
    sock.sendto(msg,addr)
    i = i+1
sock.close()
