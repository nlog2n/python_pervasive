#!/usr/bin/env python
import sys
import math
import string


##################################################
# BEGIN SUPPLIED FUNCTIONS
##################################################


##################################################
# function parse_file  
# arguments: none 
# Reads in the input from the file specified as an argument to the
# program.  NOTE: it is recommended that you edit this function to
# strip off newlines as described below.
# 
# returns: a list of all the lines in the file
##################################################
def parse_file():
  # require a filename (the name of the MSA) as an argument.
  # if it's not given, exit the program.
  # Note that sys.argv[0] is the name of the program, so 
  # sys.argv[1] is the first argument supplied
  if (len(sys.argv) != 2):
    print "Expected 1 argument, but got ", len(sys.argv)-1
    sys.exit(1)

  # read all the lines in the file given by the first argument 
  # to this script.
  input = open(sys.argv[1], 'r')
  lines = input.readlines()
  input.close()
  # lines is now a list containing each line in the MSA
  
  ## for each line, remove the "\n" return signal
  ## using the strip() function
  ## this will make your job easier later!
  newlines = []
  for myline in lines:
     myline = myline.strip('\n')
     newlines.append(myline)

  #return lines
  return newlines

##################################################
# function print_table_float
# arguments:
# D - a dictionary keyed by pairs of amino acids, e.g. 'AR'
# aas - a list of amino acid names, e.g. 'A', 'C'
# output:
# prints the values in the dictionary multiplied by 100 in a table
# format, labeled by the amino acid names.
#
# Note that this function uses 5-character-wide fields and uses 
# four characters for the number (including the decimal point)
##################################################
def print_table_float(D, aas): 
  for ki in aas: # for each amino acid, e.g. 'A'
    print "%5s" % (ki), # print the name (one the same line)
  print # that's just for a newline (\n)
  for ki in aas: # for each amino acid
    print ki, 
    for kj in aas:  # for each amino acid (inner loop) 
      if (abs(D[ki+kj]) >= 0.1 and abs(D[ki+kj]) <= 1.0): 
        print "%5.1f" % (100*D[ki+kj]), 
      elif (abs(D[ki+kj]) > 1.0): 
        print "%5.0f" % (100*D[ki+kj]), 
      else: 
        print "%5.2f" % (100*D[ki+kj]), 
    print 

##################################################
# function print_table_int
# arguments:
# D - a dictionary keyed by pairs of amino acids, e.g. 'AR'
# aas - a list of amino acid names, e.g. 'A', 'C'
# output:
# prints the values in the dictionary in a table format, labeled
# by the amino acid names.
#
# Note that in contrast to print_table_float, this function
# outputs values in %5d format (integers, 5 character-wide fields)
##################################################

def print_table_int(D, aas): 
  for ki in aas: 
    print "%5s" % (ki), 
  print 
  for ki in aas: 
    print ki, 
    for kj in aas: 
      print "%5d" % (D[ki+kj]), # print the dictionary entry for 
                                # amino acids ki, kj
    print 


##################################################
# function matrix_multiply
# arguments:
# D - a dictionary keyed by pairs of amino acids, e.g. 'AR'
# aas - a list of amino acid names, e.g. 'A', 'C'
# returns:
# a matrix that represents the matrix D times itself
##################################################
def matrix_multiply(D,AA):
  C = dict()
  for ai in AA:
    for aj in AA:
      C[ai+aj] = 0
      for ak in AA:
        C[ai+aj] += D[ai+ak]*D[ak+aj]
  return C

##################################################
# END SUPPLIED FUNCTIONS
##################################################


# create a list called AA, which will have all the amino acid names
# (when I say names, I mean single letter abbreviations)
AA = ['A','C','D','E','F','G','H','I','K','L', 
      'M','N','P','Q','R','S','T','V','W','Y'] 

## read in the msa using the supplied parse_file function
lines = parse_file()

#################### PART a ####################

# create a dictionary occ, initialize with zeros
# keys: amino acid names (i.e. single letters)
# values: number of occurrences of that amino acid
occ = dict()
for i in range(len(AA)):
  occ[AA[i]] = 0 # populate dictionary

## for each character in each line of input (lines), increment occ for
## that amino acid by one.  Also add one to a count of the total
## number of amino acids.
totalNumAA = 0
for oneline in lines :
  mylen = len(oneline)
  totalNumAA += mylen
  for i in range ( mylen ) :
    onechar =  oneline[i]
    occ[ onechar ] = occ[ onechar ] + 1
  

# create a dictionary f
# keys: amino acid names
# values: frequency of occurrence of that amino acid
f = dict()

print "Frequencies:"

## for each amino acid, save its frequency (using the f dictionary) as
## the number of occurrences divided by the total number of amino
## acids, and print the amino acid name followed by its frequency (in
## %6.4f format)
for i in range ( len(AA) ) :
  f[ AA[i] ] = float(occ[ AA[i] ]) / totalNumAA
  print AA[i] + " %6.4f" % f[ AA[i] ]




#################### PART b ####################

# create a dictionary A, initialize with zeros
# keys: pairs of amino acids, e.g. 'AD'
# values: Number of changes (aka substitutions) from amino acid 1 to 2
#         (same as 2 to 1)
A = dict()
for i in range(len(AA)):
  for j in range(len(AA)):
    A[AA[i]+AA[j]] = 0 # populate dictionary

## for each position in the length of the lines (every line has the
## same length), for every pair of amino acids at that column,
## increment A to show a mutation between them.
## NOTE: these mutations count twice for each pair because they are
## bidirectional.  Be careful not to single-count or quadruple-count
## pairs.
for i in range( len(lines) ): #oneline_i in lines :
  for j in range(len(lines)):
     if j > i :
        oneline_i = lines[i]
        oneline_j = lines[j]
        #if oneline_i != oneline_j :
        for k in range ( len(oneline_i) ) :
          onechar_i =  oneline_i[ k]
          onechar_j =  oneline_j[ k]
          if onechar_i == onechar_j :
           A[ onechar_i + onechar_j ] += 2

for i in range( len(lines) ): #oneline_i in lines :
  for j in range(len(lines)):
     if j != i :
        oneline_i = lines[i]
        oneline_j = lines[j]
        #if oneline_i != oneline_j :
        for k in range ( len(oneline_i) ) :
          onechar_i =  oneline_i[ k]
          onechar_j =  oneline_j[ k]
          if onechar_i != onechar_j :
           A[ onechar_i + onechar_j ] += 1

          



print "Number of substitutions:"

## call print_table_int with A and AA as arguments
print_table_int(A, AA)

#################### PART c ####################

# create dictionary m
# keys: amino acid names
# values: mutability of amino acid
m = dict()

## for each amino acid, record the number of times it changed into a
## different one, using A from part b).
for i in range(len(AA)):
  m [ AA[i] ] = 0 # init zero
  
for i in range(len(AA)):
  for j in range(len(AA)):
    if i != j :
      m[ AA[i] ] +=  A[ AA[i]+AA[j] ]

print "Mutabilities:"
## for each amino acid, save its mutability (the total number of
## changes divided by its total number of occurrences) in the
## dictionary m.  print its name followed by its mutability in %6.3f
## format

for i in range(len(AA) ) :
  m [ AA[i] ]  = float( m[AA[i]] ) / occ[AA[i]]
  print AA[i]+ " %6.3f" % m[ AA[i] ]


#################### PART d ####################

# create variable Lambda
myLambda = 0

## Create a temporary variable.  
## For each amino acid, add its frequency times its mutability to the
## temporary variable.  Set Lambda to 0.01 divided by that temporary
## variable.

## print 'Lambda = ' followed by the Lambda you calculated, in %10.8f
## format.
tmpVar = 0
for i in range (len(AA)) :
  tmpVar = tmpVar + f[ AA[i] ] * m[ AA[i] ]
myLambda = 0.01 / tmpVar
print "Lambda = %10.8f" % myLambda


#################### PART e ####################

# create the dictionary of substitution probabilities for pairs of
# amino acids.  
# keys: amino acid pairs, e.g. 'RG'
# values: probability of substitution from one amino acid to the other
SubM = dict()


for ai in AA:
  for aj in AA: # iterate over pairs (ai,aj) amino acid letters
    if ai == aj:
      ## for each pair of amino acids, call them amino acid i and j, if both
      ## are the same amino acid (i == j) then: set the substitution
      ## probability (in SubM) to 1 - Lambda * the mutibility of the amino
      ## acid.
      SubM [ ai + aj ] = 1 - myLambda * m [ ai ]
      
    else:
      ## If instead the two amino acids are different: Recall that A (your
      ## dictionary from part c) has the number of times i replaces j in the
      ## alignment.
      
      denominator = 0
      ## for each amino acid k, where k is not j, add A[k+j] to
      ## denominator.  Set the substitution probability (in SubM)
      ## from i to j to be (Lambda * the mutability of j * A[i+j]
      ## / denominator)
      for ak in AA :
      	if ak != aj :
      		denominator += A[ ak + aj ]
      		SubM[ ai + aj ] = myLambda * m [aj] * A[ ai + aj ] / denominator

print "Substitution probabilities (t = 1):"

## call the print_table_float function, passing SubM and AA
print_table_float( SubM, AA )

#################### PART f ####################

## use the matrix_multiply function to square your substitution
## probability matrix (SubM) five times, using a loop.
i=0
while i < 5 :
  SubM = matrix_multiply( SubM, AA )
  i = i+ 1
  
print "Substitution probabilities (t = 5):"

## call the print_table_float function, passing your new substitution
## dictionary and AA
print_table_float( SubM, AA )
