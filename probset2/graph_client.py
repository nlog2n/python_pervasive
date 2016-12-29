#! /opt/sfw/bin/python

# 6.894 problem set 2 - to find the path between 2 points in graph
# client side program
# created by Fang Hui 2004.9.29

# bug fix 9.30:
#     there seems to be problem in using "clear" or "remove" methods
#     on LIST in function find_path( ):sometimes return surplus path
#     after reaching end-point. so I just give a direct empy value 
#     where necessary.
#     
#     Line 71: "for y in newpath :
#                   newpath.remove(y)
#              " replaced by " newpath = []"

# improvements:
#    * more flexible user input.case-insensitive,blank tolerant
#      but some version of python may not support


import sys
import string
import socket

# to be general , I store both non-directional and directional graphs as
# a directional graphs,where graph is a dictionary, each element name is
# vertex, and its value is all vertexes connected to itself.
# one sample :
# graph = {    'A': ['B', 'C'],
#             'B': ['A', 'G','F'],
#             'C': ['A','G','D'],
#             'D': ['C','E','I'],
#             'E': ['D'],
#             'F': ['B','H'],
#             'G': ['B','C','H'],
#             'H': ['F','G','I'],
#             'I': ['D','H','J'],
#             'J': ['H','I','K'],
#             'K': ['J']}


#  find the shortest path from start point to end point.
#  actually the method can find the shortest path from
#  any point to a certain end point.
def find_path(graph, start, end):
      points = graph.keys()
      path   = {}
      # init
      for i in points:
          path[i] = []
          if i == end:
            path[i].append(i)
          if  end in graph[i] :
            path[i].append(end)
            path[i].append(i)

      found = 1
      while  found :
        # find the shortest point from the first set
        found = 0
        min_newpath= None        
        for i in points:
          if  not path[i] : # not yet in shortest set
              newpath = []
              for x in graph[i]:
                 if  path[x] : # already in shortest set:
                    if  len(newpath)==0 or  (len(newpath)!=0 and len(path[x])+1) < len(newpath) :
                      #for y in newpath :
                       #   newpath.remove(y)
                      newpath = []
                      for y in path[x]:
                          newpath.append(y)
                      newpath.append(i)
              if newpath :
                 if  not min_newpath or len(newpath) < len(min_newpath)  :         
                     min_newpath= newpath
        
        if min_newpath :
           #print min_newpath
           path[min_newpath[len(min_newpath)-1]] = min_newpath
           found= 1

      a = path[start]
      a.reverse()
      return a

      
# Main program entrance

if len(sys.argv) < 4: 
    print "usage: graph_client.py <address> <port> <map>"
    sys.exit(2)

# read file from commandline
# the map file format : (AB,AC,BF,BG,CD,DI,DE,IJ,HI,CG,GH,FH,HJ,JK)
f=open(sys.argv[3], 'r')
str = f.read()
#str.lower()  # don't care upper/lower case
#str.strip()  # remove whiteblank from left ,right sides
print "Map is:%s" % (str)
f.close()

# parse the string into graph data structure
str = str[1:-1]                #strip first and last quote
z = string.split(str,',')  #split by coma ','
graph = {}
for x in z:                #get each edge from the input string file
   if (not graph.has_key(x[0]) ) :
       graph[x[0]] = []
   graph[x[0]].append(x[1])
   if (not graph.has_key(x[1]) ) :  # bi-directional
       graph[x[1]] = []
   graph[x[1]].append(x[0])

#print graph   
# find out the start point and ending point
points = graph.keys()
points.sort()
start_point = points[0]
end_point   = points[len(points)-1]
print  "Start point is:%s , and end point is:%s" %(start_point,end_point)

answer =  find_path(graph, start_point, end_point)
print "Find the path: %s" % answer

# send the answer to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect( (sys.argv[1], int(sys.argv[2]) ) )
print "Connected and sending..."
for node in answer :
   s.send(node)

print "Completed!"