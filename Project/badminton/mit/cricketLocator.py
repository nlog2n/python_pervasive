#!/usr/bin/python

import string
import socket
import sys
import time
import math

class cricketLocator:
#Sets up socket to communicate with cricket
#def __init__(self):
	def __init__(self):
		host="127.0.0.1"
		port=2947
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        	self.socket.connect((host,port))
		self.socket.send("r\n")
	
	def cricketClose(self):
		self.socket.close()
			
#Returns absolute position as viewed from cricket 
	def getData(self, name):
		line=""
		while (("DB" not in line) or (name not in line)):
			line = self.socket.recv(1024)
			if (string.find(line, "\n") > 0):
				line=line[string.find(line, name):]
				line=line[:string.find(line, "\n")]
		dist=line[string.find(line,"DB")+3:]
		if (string.find(dist, ",")>0):
			dist=dist[:string.find(dist,",")]
		return int(dist)
		
#Returns absolute position as viewed from NUS cricket 
	def getNusData(self):
		line=""
		while (('dist=' not in line) or ('duration' not in line)):
			line = self.socket.recv(1024)
			if (string.find(line, "\n") > 0):
				line=line[string.find(line, 'dist='):]
				line=line[:string.find(line, "\n")]
		dist=line[string.find(line,"dist")+5:]
		if (string.find(dist, ",")>0):
			dist=dist[:string.find(dist,",")]
			print 'Distance recorded: ', dist
		return int(dist)		

# initializes listen cricket to be a listener with name "main"
# returns nothing
	def initListenCricket(self, name):
		self.initCricket(name,1)
		
# initializes left cricket to be a beacon with name "left"
# returns nothing
	def initLeftCricket(self):
		self.initCricket("left",0)
		
# initializes right cricket to be a beacon with name "right"
# returns nothing
	def initRightCricket(self):
		self.initCricket("right",0)
		
# initializes cricket to be a beacon with id "name"
# if i==0, set up cricket as beacon and a listener otherwise
# returns nothing
	def initCricket(self, name, i):
		data="P SP "+ name+"\n"
		self.socket.send(data)
		time.sleep(.2)
		if (i==0):
			self.socket.send("P MD 1\n")
		else:
			self.socket.send("P MD 2\n")
		time.sleep(.2)
		self.socket.send("P SV\n")
		time.sleep(.2)
		print "DONE!"

	def calibrateLeft(self):
		hyp=-1
		self.h=0
		while (self.okay(hyp, self.h)==0): 	
			self.h=self.getData("left")-10
			hyp=self.getData("right")
			print "Left= ", self.h
			print "Right= ", hyp
		print "HYP", hyp
		print "height", self.h
		self.c=round(math.sqrt(hyp*hyp - self.h*self.h))	
		print "Calibration of left - DONE!"
		
	def calibrateRight(self):
		hyp=-1
		self.h=0
		while (self.okay(hyp, self.h)==0):
			self.h=self.getData("right")
			hyp=self.getData("left")
		print "HYP", hyp
		print "height", self.h
		self.c=round(math.sqrt(hyp*hyp - self.h*self.h))	
		print "Calibration of right - DONE!"
		
	def getHeight(self):
		return self.h
	
	def  getCricketDistance(self):
		return self.c
		
	def getX(self):
		return self.x
		
	def getY(self):
		return self.y
		
	def okay(self, a, b):
		if (a < b):
			return 0
		return 1
			
	def getLocation(self):
		correct=.1
		a_tmp=-2
		b_tmp=-1;
		while (a_tmp<self.h or b_tmp<self.h):
			a_tmp=self.getData("left")
			b_tmp=self.getData("right")
			print "Left= ",a_tmp
			print "Right= ",b_tmp
			print "Height= ",self.h
			if (a_tmp*(1-correct)<= self.h):
				a_tmp=self.h-1
			if (b_tmp*(1-correct)<= self.h):
				b_tmp=self.h-1	
		a=round(math.sqrt(a_tmp*a_tmp-self.h*self.h))
		b=round(math.sqrt(b_tmp*b_tmp - self.h*self.h))
		[self.x,self.y]=self.getXandY(a,b,self.c)
		return [self.x,self.y]
			
	def getXandY(self,sideA, sideB, fixedSideC):
   		a = sideA
     		b = sideB
    		c = fixedSideC
    		x = (a*a+c*c-b*b)/(2*c)
    		tempy2 = a*a-x*x
		if (tempy2 >=0):
    			y = math.sqrt(tempy2)
    			x = round(x)
    			y = round(y)
    			return [x, y]	
		else:
			return [0,0]
