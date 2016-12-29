#! /opt/sfw/bin/python

# 6.894 problem set 2 - to find the path between 2 points in graph
# client side program
# Fang Hui 2004.9.29

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

def find_path(graph, start, end, path=[]):
        path = path + [start]
        if start == end:      # the path is itself
            return path
        if not graph.has_key(start):  # this start point is seperate alone
            return None
        found = None
        for point in graph[start]:  # Check all the points connected to start
            if point not in path:   # this point not yet in shortest-path set
                candidatePath = find_path(graph, point, end, path)
                if candidatePath:
                    if not found or len(candidatePath) < len(found):
                    # Try to choose the path start->point->end 
                    # instead of start->end if shorter
            # the minimum path point connected to start will be choosed out
            # when "for" finished
                        found = candidatePath
        return found


# Main program entrance

if len(sys.argv) < 4: 
    print "usage: graph_client.py <address> <port> <map>"
    sys.exit(2)

# read file from commandline
# the map file format : (AB,AC,BF,BG,CD,DI,DE,IJ,HI,CG,GH,FH,HJ,JK)
f=open(sys.argv[3], 'r')
str = f.read()
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
for node in answer:
      s.send(node)

print "Completed!"