#!/usr/bin/env python
import sys
import math

def parseArgs():

    if len(sys.argv) < 3:
        print "Expected at least 3 arguments, but only got", len(sys.argv)-1
        sys.exit()

    motif_fn, seq_fn, threshold = sys.argv[1:]

    return motif_fn, seq_fn, float(threshold)

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

def parsePSSM(fn):

    # initialize the model - an list of positions
    model = []

    fh = open(fn, 'r')
    for line in fh.readlines():
        line = line.strip()
        if not line: continue
        # skip the header
        if line.startswith('log'): continue
        position = line.split()
        if len(position) != 4:
            print("Error: Expect exactly 4 nts per position, but found",
                  len(position))
            sys.exit()
        # represent each position as a dictionary
        # keys = possible nucleotides, values = log odds scores
        model.append({'A': float(position[0]),
                      'C': float(position[1]),
                      'G': float(position[2]),
                      'T': float(position[3])})
    fh.close()

    return model

def calculateMaxMinMotifScores(model):

    # initialize min and max motif scores
    minScore, maxScore = 0, 0
    
    ## for every position in the motif
    ## add to the min and max scores using the model
    for i in model:
        minScore += min( i['A'], i['C'], i['G'], i['T'])
        maxScore += max( i['A'], i['C'], i['G'], i['T'])
    return minScore, maxScore

def searchForMotif(seq, model, minScore, maxScore, threshold):

    # initialize a list of motif occurrences
    motifs = []

    ## for every possible offset in the sequence
    ## initialize the total motif score
    ## score every motif position using the model to get a total motif score
    ## determine if raw score is above input threshold
    ## if so, add a tuple to the motifs list containing 
    ## (start position of motif in seq, 
    ## motif seq, 
    ## score, 
    ## score as fraction of best score)

    cutoff = minScore + threshold* (maxScore - minScore)
    #print cutoff, minScore, maxScore

    for i in range( len(seq) ) :

         if i <= len(seq) - len(model)  :  # tail not enough length as a motif
            rawScore = 0
            k = 0 
            subSeq = ""
            while k < len(model) :
              char  = seq[ i + k]   # ACGT
              rawScore += model [ k ] [ char ]
              subSeq += char
              k = k+1

            if  rawScore > cutoff :
              scoreFraction = (rawScore - minScore) / ( maxScore -minScore)
              motifs.append( ( i, subSeq, rawScore, scoreFraction) )
              #print i, subSeq, rawScore, scoreFraction, "found."
    return motifs

def writeOutput(motifs):

    # create an output file handle
    fh = open('motifFinderOutput.txt', 'w')

    # output each motif
    for motif in motifs:
        fh.write('%s %s %.1f %.2f\n' %motif)

    fh.close()

def run():

    ## parse command line arguments
    (motifFile, seqFile, threshold) = parseArgs()
    ## parse the fasta sequence file
    seq =   parseFasta(seqFile)
    ## parse the motif file
    model = parsePSSM( motifFile)
    ## calculate the max and min score for this PSSM
    (minS, maxS) = calculateMaxMinMotifScores( model)
    ## search for motif occurences above threshold score
    motifs = searchForMotif(seq, model, minS, maxS, threshold)
    ## write motifs to output file
    writeOutput(motifs)

    return

run()

