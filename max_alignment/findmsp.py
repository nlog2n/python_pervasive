#!/usr/bin/env python
import sys

def parseArgs():

    if len(sys.argv) < 3:
        print "Expected at least 3 arguments, but only got", len(sys.argv)-1
        sys.exit()

    query_fn, db_fn, penalty = sys.argv[1:]

    return query_fn, db_fn, int(penalty)

def parseFasta(fn):

    seq = ''

    fh = open(fn, 'r')
    fastaHeader = False
    for line in fh.readlines():
        line = line.strip()
        if not line: continue
        if line.startswith('>'):
            if fastaHeader:
                print "Error: Assume only one sequence in input fasta file"
                sys.exit()
            fastaHeader = True
            continue
        seq += line.upper()
    fh.close()

    return seq

def findMSP(querySeq, dbSeq, penalty):

    # initialize global variables 
    qLen = len(querySeq)   # length of query sequence
    dbLen = len(dbSeq)     # length of database sequence
    maxScore = 0           # score of best align seed so far
    maxAlignLen = 0        # length of best align so far
    alignStartInQuery = 0  # start position in query of best align
    alignStartInDB = 0     # start position in database of best align

    ## for every possible offset in the database
    for offset in range ( dbLen ) :
    
      # initialize local alignment variables
      currAlignStartInQuery = 0 # start position in query of current align
    
      ## for every position in the query
      ## check if query nt matches db nt
      while currAlignStartInQuery < qLen :
        minScore = 0              # min score for this align so far
        currScore = 0             # score of current align being evaluated
 
        i = 0
        while i < qLen and offset+i < dbLen and currAlignStartInQuery +i < qLen :
         
          ## if so, increment current alignment score (match score +1)
          if dbSeq[ offset + i] == querySeq[ currAlignStartInQuery + i ] :
            currScore = currScore + 1
            ## check if have a new max diff between current score and min score
            ## if so, update global variables
            if currScore - minScore > maxScore : 
              maxScore = currScore - minScore
            #if currScore > maxScore : 
              #maxScore = currScore
              maxAlignLen = i + 1
              alignStartInQuery = currAlignStartInQuery
              alignStartInDB = offset

          ## otherwise, subtract mismatch penalty
          else :  # no match then break
            currScore = currScore + penalty
            if currScore < minScore :         ## check for a new minimum score
                minScore = currScore 
            break
          i = i + 1
  
        currAlignStartInQuery = currAlignStartInQuery + 1

    return (alignStartInQuery, alignStartInDB, maxAlignLen, maxScore)

def writeOutput(querySeq, queryPos, dbSeq, dbPos, maxLen, maxScore):

    fh = open('findMSPoutput.txt', 'w')
    # output the stats
    fh.write("Match score: %s\n" %maxScore +
             "Match length: %s\n" %maxLen +
             "Position in query: %s\n" %queryPos +
             "Position in database: %s\n" %dbPos)
    # output the alignment
    alignmentString = ""
    for i in range(0, maxLen):
        if (querySeq[queryPos+i] == dbSeq[dbPos + i]):
            alignmentString += "|"
        else:
            alignmentString += " "
    fh.write(querySeq[queryPos:queryPos + maxLen] + '\n' + 
             alignmentString + '\n' + 
             dbSeq[dbPos:dbPos + maxLen] + '\n')
    fh.close

def run():

    ## parse command line arguments
    (query_fn, db_fn, penalty) = parseArgs()
    ## parse the query fasta file
    query_seq = parseFasta( query_fn )
    ## parse the database fasta file
    db_seq = parseFasta( db_fn)

    ## find the MSP
    (query_pos, db_pos, maxLen, maxScore) = findMSP(query_seq, db_seq, penalty)
    
    ## write the MSP to output file
    writeOutput(query_seq, query_pos, db_seq, db_pos, maxLen, maxScore)    
    
    return

run()
