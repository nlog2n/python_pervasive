# Modified by fanghui 2004.10


import os
import math


class Vertex:
#  class data members include:
#  id,x,y,name , in_edges,out_edeges

    def __init__(self, id):
        self.id = id
        self.x  = 0
        self.y  = 0
        self.name = ""
        self.in_edges=[]
        self.out_edges = []

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

class Edge:
    def __init__(self, v1, v2, weight=0):
        self.v1 = v1
        self.v2 = v2
        self.weight = weight

    def set_weight(self, weight):
        self.weight = weight

    def get_weight(self):
        return self.weight

class Graph:
    def __init__(self, vertices = {}, edges = []):
        self.vertices = vertices
        self.edges = edges
        self.vertex_radius = 5

    def get_edges(self):
        return self.edges[:]

    def get_vertices(self):
        return self.vertices.values()

    def add_vertex(self, id, x, y,name):
        """creates a vertex with the specified id and adds it to the graph with
        no edges.  returns the created vertex
        """
        while self.vertices.has_key( id ):
            v = self.vertices[id]
            if   v.x == int(x) and v.y == int(y) :
                  raise ValueError("duplicate vertex")
                  return
            else  :
                  id = id + 1
              
        new_vertex = Vertex( id )

        new_vertex.x = int(x)
        new_vertex.y = int(y)
        new_vertex.name = name

        self.vertices[id] = new_vertex
        return new_vertex

    def get_vertex(self, id):
        return self.vertices[id]

    def has_vertex(self, id):
        return self.vertices.has_key(id)

    def has_edge(self,v1,v2):
        for x in self.edges :
           if x.v1==v1 and x.v2== v2 :
              return True
        return False


    def cast_ray(self, x, y):
        min_dist = self.vertex_radius * self.vertex_radius
        
        for v in self.vertices.values():
            dist = (v.x - x)*(v.x-x) + (v.y-y)*(v.y-y)
            if dist < min_dist: return v

        return None


    def find_vertex(self, x, y):
        if len(self.vertices) == 0: return None
        closest = None 
        closest_dist = -1   # self.vertex_radius  * self.vertex_radius 

        for v in self.vertices.values():
            dist = (v.x - x)*(v.x-x) + (v.y-y)*(v.y-y)
            if closest is None or dist < closest_dist:
                closest = v
                closest_dist = dist
        return closest


 
    def remove_vertex(self, id):
        """removes the specified vertex from the graph.
        """
        v = self.vertices[id]
        to_be_deleted = []
        for e in self.edges :
            if e.v1== v or e.v2== v:
                to_be_deleted.append(e)

        to_be_deleted2 =[]
        for e in self.edges :
           for e2 in to_be_deleted :
             if e.v1==e2.v2 and e.v2==e2.v1 :
                  to_be_deleted2.append(e)
                  break
           
        i = 0
        to_be_deleted =  to_be_deleted + to_be_deleted2
        for e in to_be_deleted :
            if e.v1== v :
                v2 = e.v2
            if e.v2== v :
                v2 = e.v1
            if v in v2.in_edges :
                v2.in_edges.remove(v)
            if v in v2.out_edges :
                v2.out_edges.remove(v)


        for e in to_be_deleted :
            if e in self.edges :
               self.edges.remove(e)
            i=i+1
            print "i=%d" % i
            
        del self.vertices[id]

    def remove_edge(self, v1,v2):
        """removes the specified edge from the graph"""
        # delete v1->v2 and v2->v1 samely
        for e in self.edges :
           if (e.v1==v1 and e.v2== v2) or ( e.v1==v2 and e.v2==v1):
               self.edges.remove(edge)

    def add_edge(self, v1, v2, weight=0):
        """creates an edge from v1 to v2 with the specified weight, and adds it
        to the graph.  returns the created edge
        """
        e = Edge(v1, v2, weight)
        v1.out_edges.append(e)
        v2.in_edges.append(e)
        self.edges.append(e)
        return e


    def weight(self, v1, v2):
       return math.sqrt((v1.x-v2.x)*(v1.x-v2.x) + (v1.y-v2.y)*(v1.y-v2.y))




    # created by fanghui : to clear all the vertexes and edges.2004.10.1
    def clear(self) :
        self.vertices.clear()
        self.edges = []



    #  find the shortest path from start point to end point.
    #  actually the method can find the shortest path from
    #  any point to a certain end point.
    def find_path2(self, start, end):

      path   = {}
      # init
      for i in self.vertices:
          path[i] = []
          if i == end:
            path[i].append(i)
          if  self.has_edge(i,end):
            path[i].append(end)
            path[i].append(i)

      found = 1
      while  found :
        # find the shortest point from the first set
        found = 0
        min_newpath= None        
        for i in self.vertices :
          if  not path[i] : # not yet in shortest set
              newpath = []
              for x in self.vertices :
                 if self.has_edge(i,x):
                  if  path[x] : # already in shortest set:
                    if  len(newpath)==0 or  (len(newpath)!=0 and len(path[x])+1) < len(newpath) :
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

      print path
      a = path[start]
      a.reverse()
      return a


    def find_path(self,v1,v2,path=[]) :
      path = path + [v1]
      if v1==v2 :
         return path
      if not self.has_vertex(v1.id):
         return None
      found = None
      for e in v1.out_edges :
         node = e.v2
         if node not in path :
            newpath= self.find_path(node,v2,path)
            if newpath :
               if not found or len(newpath) < len(found) :
                  found = newpath
      return found



    def load(self ,  filename):
       if filename is not None and  os.path.exists(filename):
          try:
             self.clear()

             f = file(filename)

             while True:
                s = f.readline()
                if len(s) == 0: break
                s = s.strip()
                if s[:6] == "vertex":
                    items = s.split(',')
                    id = items[1]
                    x = items[2]
                    y = items[3]
                    name = ""
                    if len(items) > 4:
                        name = items[4]
                    new_vertex = self.add_vertex(id,x,y,name)

                elif s[:4] == "edge":
                    junk, vid1, vid2 = s.split(',')
                    try:
                        v1 = self.get_vertex(vid1)
                        v2 = self.get_vertex(vid2)
                        self.add_edge( v1, v2, self.weight( v1, v2 ) )
                        self.add_edge( v2, v1, self.weight( v2, v1 ) )
                    except:
                        print "bad edge (%s, %s)" % (vid1, vid2)

             f.close()
             return True
          except IOError, e:
            print e
            return False
       else :
          return False

    def save(self, filename):

        try:
            f = file(filename, "w")
            i = 0
            for v in self.vertices.values():
                v.id = i
                f.write("vertex,%s,%s,%s,%s\n" % (v.id, v.x, v.y, v.name))
                i = i + 1

            for e in self.edges:
                f.write("edge,%s,%s\n" % (e.v1.id, e.v2.id))
            f.close()
            return True
        except IOError, e:
            print e
            return False
      
