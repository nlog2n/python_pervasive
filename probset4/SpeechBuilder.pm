############################################################################
#    (c) Copyright 1999 - 2000 M.I.T.  Permission is hereby granted,       #
#    without written agreement or royalty fee, to use, copy, modify, and   #
#    distribute this software and its documentation for any purpose,       #
#    provided that the above copyright notice and the following three      #
#    paragraphs appear in all copies of this software.                     #
#                                                                          #
#    IN NO EVENT SHALL M.I.T. BE LIABLE TO ANY PARTY FOR DIRECT,           #
#    INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT   #
#    OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF            #
#    M.I.T. HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.            #
#                                                                          #
#    M.I.T. SPECIFICALLY DISCLAIMS ANY WARRANTIES INCLUDING, BUT NOT       #
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A  # 
#    PARTICULAR PURPOSE, AND NON-INFRINGEMENT.                             #
#                                                                          #
#    THE SOFTWARE IS PROVIDED ON AN "AS IS" BASIS AND M.I.T. HAS NO        #
#    OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS,    #
#    OR MODIFICATIONS.                                                     #
############################################################################



# SpeechBuilder Package

# Contains functions for outputting responses and/or history lines,
# as well as parsing frames to hash trees and unparsing hash trees to
# frames.

package SpeechBuilder;


# output
# Outputs a text string and an optional history line to the SpeechBuilder
# backend server. Automatically strips extra carriage returns and adds
# one if needed, and adds the history= prefix.
#      SpeechBuilder->output("Welcome to SpeechBuilder.");
#      SpeechBuilder->output("Welcome to SpeechBuilder.", "(target=none)');

sub output {
    my $response = shift; # The response to speak.
    my $history = shift;  # The history variable to report, if any.
    
    # Print the history string if it was passed.
    if (defined($history)) {
	chomp $history;
	print "history=$history\n";
    }
    # Print the response string.
    chomp $response;
    print "$response\n";
}


# parse
# Parses a frame structure from the SpeechBuilder CGI argument into a hash
# tree, returning a hash.
#      my %frame = SpeechBuilder->parse(param('frame'));

sub parse {
    my $frame = shift;                     # The frame to parse.
    my @frame = split(/([(,=)])/, $frame); # The split up frame array.

    # Split the frame on parentheses, commas, and equals, and pass it to
    # the recursive parser, taking the resulting reference and returning
    # the actual hash table.
    return %{parse_recurse(@frame)};
}


# unparse
# Takes a hash tree and generates a valid frame, usually to be used as a
# history string and to be later parsed to regain the original structure.
#      my $history = SpeechBuilder->unparse(%history);

sub unparse {
    my %data = @_;  # The hash structure to unparse.
    my $text = "("; # Start out with open parenthesis.
    my $first = 1;  # Flag to note that this is the first key at
                    # the current level (and so gets no comma before it).
    
    # Run through the keys, stringing them together with commas.
    foreach my $key (sort(keys(%data))) {
	$text .= "," unless $first;
	$first = 0;
	# If a key is a reference (hierarchical), recursively unparse it.
	if (ref($data{$key})) {
	    $text .= "$key=".unparse(%{$data{$key}});
	} else {
	    $text .= "$key=$data{$key}";
#	    print "terminated at $key=$data{$key}\n";
	}
    }
    # Return the final result, with closing parenthesis.
    return $text.")";
}


# parse_recurse
# Used recursively by parse and itself to parse frame. Do not call this
# function directly -- use parse.

sub parse_recurse {
    my @frame = @_;    # Split up frame.
    my %frame = ();    # Hash table of current level of structure.
    my $depth = 0;     # Depth within current level 
                       # (0=outside, 1=inside, 2=substructure).
    my $lastkey = "";  # Previous key encountered (key=)
    my $lastword = ""; # Previous segment of frame.
    my @subframe = (); # List of segments contained in lower hierarchy to
                       # be recursively parsed.
    my $building = 0;  # Flag if we're inside recursive structure (and
                       # building @subframe).
    
    # Deal with each segment in turn.
    foreach my $segment (@frame) {
	# Skip blank segments.
	next if ($segment eq '');

	# If we hit a '=', record the previous segment as being our
	# key or h-key.
	$lastkey = $lastword if (!$building && $segment eq '=');
	
	# If we have reached a second open paren, then start recording keys at
        # the next level of hierarchy.
	if ($segment eq '(') {
	    $depth++;
	    if ($depth == 2) {
		@subframe = ();
		$building = 1;
	    }
	}
	
	# If building a subframe, add the gurrent segment to the list to
	# be recursively processed at the closing parenthesis.
	push @subframe, $segment if ($building);

	# If we have a string (not open paren) and previous segment was '=',
	# we have a key/value pair to record.
	if (!$building && $segment ne '(' && $lastword eq '=') {
	    
	    $frame{$lastkey} = $segment;
	}

	# If we have hit the end of a segment, lower our depth. If that was
	# depth 1, we're done. Otherwise, we finished a recursive subframe,
	# and we need to recurse on it.
	if ($segment eq ')') {
	    $depth--;
	    if ($depth == 0) {
		return \%frame;
	    } elsif ($depth == 1) {
		$frame{$lastkey} = parse_recurse(@subframe);
		$building = 0;
	    }
	    
	}
	
	# Record this segment as being the most recent.
	$lastword = $segment;
    }
    
    # Return a reference to our newly created (sub)frame.
    return \%frame;
}


1;
