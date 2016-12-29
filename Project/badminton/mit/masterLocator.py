#!/usr/bin/python 
#Master Locator

#requirements : 
#IP of this computer
#IP of gui server

import string
from socket import *
import math
import random
from configure import *



if "MIT" == network_side:
    port_gui_0 = port_gui0_location0
    port_gui_1 = port_gui1_location0
    port_masterlocator = port_masterlocator0
    port_querylocator = port_querylocator0
else:
    port_gui_0 = port_gui0_location1
    port_gui_1 = port_gui1_location1
    port_masterlocator = port_masterlocator1
    port_querylocator = port_querylocator1

g_addr_0 = (host_game_engine, port_gui_0)
g_addr_1 = (localhost, port_gui_1)

queryAddr = (localhost, port_querylocator)

buf = 1024

sock = socket(AF_INET,SOCK_DGRAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
sock.bind((localhost, port_masterlocator))

# print "Master locator binds with port " + str(port_masterlocator)
data=''


# Set up gui socket

g_sock_0=socket(AF_INET,SOCK_DGRAM)
g_sock_1=socket(AF_INET,SOCK_DGRAM)
    
if "MIT" == network_side:
    g_sock_1.bind((localhost, port_gui_1))
    print "MIT master locator waiting for NUS gui at port " + str(port_gui_1)
    data, g_addr_1 = g_sock_1.recvfrom(buf)
    print "MIT master locator at side " + network_side + " print: receive a request from NUS server"

g_sock_0.sendto("connected from master Locator at site" + network_side, g_addr_0)
g_sock_1.sendto("connected from master Locator at site" + network_side, g_addr_1)    
 



#absolute current position
pos=[0,0]
#current player location state
CR=[0,0,0,0]	

#counter of messages
num=0

#How often we update the gui
freq=10

#fixed cricket locators
cricketWidth=520
cricketHeight=670

def recalcPos():
	a = CR[0] * scale
	b = CR[1] * scale
	c = cricketWidth
	x = (a*a+c*c-b*b)/(2*c)
	print x
	print a
	if (a*a-x*x >=0):
		y = math.sqrt(a*a-x*x)
		pos[0] = int(round(x))
		pos[1]= int(round(y))
#	pos[0]=random.randint(0,500)
#	pos[1]=random.randint(0,500)
		
sock.settimeout(.05)
while 1:
	#comment this line out to avoid updating the gui for now
	num=num+1
	
	#now send updated location to gui
	if num==freq:
		num=0
		g_msg= str(pos[1])+','+str(pos[0])+'\n'
		g_sock_0.sendto(g_msg,g_addr_0)		
		g_sock_1.sendto(g_msg,g_addr_1)
		recalcPos()
		# print "master locator at side " + network_side + "  print: sending to gui" + g_msg
		
	data=''
 	while (data ==''):
		try:
			data, addr=sock.recvfrom(buf)
                        print "Master Location print: Data recv - ", data
		except:
			#send new request and wait for reception
			data='n'
	
	if '<' == data[0]:
		#information on new location
		index=int(data[string.find(data,'>')-1:string.find(data,'>')])
		data=string.replace(data,'\n','')
		CR[index]=int(data[string.find(data,'D=')+2:])
		recalcPos()
		print "master locator at side " + network_side + "  print: Data recv at index -" , index , "with reading" , CR[index]
	
	if '?' == data[0]:
		data=string.replace(data,'\n','')
		t_sock=socket(AF_INET,SOCK_DGRAM)
		# t_sock.connect(addr)
		t_msg='<MasterLocator>' + str(pos[0]) + ',' + str(pos[1])
		print "master locator at side " + network_side + "  print: sent ", t_msg
		t_sock.sendto(t_msg,queryAddr)
		t_sock.close()

sock.close()
g_sock_0.close()
g_sock_1.close()	
