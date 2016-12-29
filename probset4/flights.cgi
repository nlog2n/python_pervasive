#!/usr/local/bin/perl -I/server/sls/Galaxy/SLS-Lite/0.07/perl

##############################################################
#                                                            #
#  	Copyright (c) 2000                                   #
#                                                            #
# 	Spoken Language Systems Group                        #
#                                                            #
# 	Laboratory for Computer Science                      #
#                                                            #
# 	Massachusetts Institute of Technology                #
#                                                            #
# 	All Rights Reserved                                  #
#                                                            #
##############################################################

#  This is an example back-end script for the SpeechBuilder
#  application. It works with the 'flights' domain defined in the
#  flights.xml document that is enclosed in the tar file. Please refer to
#  the README file for more information on how to set up the 'flights'
#  domain on the web page and begin using your application. This script
#  parses the action and semantic frame information given to it by the
#  runtime module which is configured on the SpeechBuilder web page.
#  Here are some examples of valid queries for this script:

#  action=list&frame=(destination%3dSFO,origin%3dBOS)
#  action=list&frame=(departure_time%3d(weekday%3dmonday))&history=(destination%3dSFO,origin%3dBOS)
#  action=list&frame=(arrival_time%3d(relative%3dafter,time%3d(hour%3d11,minute%3d02,xm%3dAM)))&history=(departure_time=(weekday=monday),destination=SFO,origin=BOS)



$LOGFILE = "flights.log";

open LOG, ">> $LOGFILE";
print LOG localtime().": GET $ENV{REQUEST_URI}\n";
close LOG;


# Use the CGI package.
use CGI qw(:standard :html -debug);
use CGI::Carp 'fatalsToBrowser';

# Use the SpeechBuilder helper package
use SpeechBuilder;

print header;

# Get the action of the query.
$action = param('action');

# Get and parse the frame
my $frame = param('frame');
my %frame = SpeechBuilder::parse(param('frame'));


# Get and parse the history
my $history = param('history');
my %history = SpeechBuilder::parse(param('history'));

# Just some sample city codes (don't forget to change the vocabulary on the
# web page if you change these, and vice versa)
my %city_codes = (
    'BOS' => 'boston',
    'SFO' => 'san francisco',
    'NYC' => 'new york',
    );


my $output = '';
my $error = '';

if($action =~ /###call_answered###/) {         # just picked up, say hello
    $output = "Welcome to the flight assistant.\n";
} elsif ($action eq "PARAPHRASE_FAILED") {     # system did not understand
    $output = "I'm sorry, I didn't understand you.\n";
} elsif($action =~ /^goodbye/i) {              # say good bye
    $output = "###close_off###Good bye.\n";
} elsif($action =~ /^unknown/i) {              # action unknown, say pardon me
    $output = "Pardon me?\n";
} else {
    $output = '';

    
    # This part gets information out of the history if it was not specified
    # in the current query. This is so the user doesn't have to repeat
    # information. For example, they can say:
    # "I want to fly from New York to Boston on Wednesday"
    # and then they are able to say
    # "How about on Thursday"
    # So here, the information about their origin and destination is 
    # obtained from the history.

    if (!($frame{'arrival_time'} || $frame{'departure_time'})) {
	if ($history{'arrival_time'}) {
	    $frame{'arrival_time'} = $history{'arrival_time'}
	}
	if ($history{'departure_time'}) {
	    $frame{'departure_time'} = $history{'departure_time'};
	}
    }

    if ((!$frame{'origin'}) && $history{'origin'}) {
	$frame{'origin'} = $history{'origin'};
    }

    if ((!$frame{'destination'})  && $history{'destination'}) {
	$frame{'destination'} = $history{'destination'};
    }

	
    # Get the arrival and departure time structures into a hash
    %arrival_time = %{ $frame {'arrival_time'} };
    %departure_time = %{ $frame {'departure_time'} };

    # Get the destination and origin
    $destination = $frame{'destination'};
    $origin = $frame{'origin'};

    if ((!$origin) || (!$destination)) {
        $error = "Please specify the origin and destination cities.\n";
    }

    
    # Put together the origin and destination
    $output = "You want to fly from ".$city_codes{$origin}.
	" to ". $city_codes{$destination}." ";


    # Figure out when they want to fly
    if (%arrival_time) {
	$output .= "arriving ";
	$relative = $arrival_time{'relative'};   # Before or after
	%time = %{ $arrival_time{'time'} };      # Get the time structure
	$time_of_day = $arrival_time{'time_of_day'};    # Time of day
	$weekday = $arrival_time{'weekday'};     # or weekday
    } elsif (%departure_time) { 
	$output .= "leaving ";
	$relative = $departure_time{'relative'};
	%time = %{ $departure_time{'time'} };
	$time_of_day = $departure_time{'time_of_day'};
	$weekday = $departure_time{'weekday'};
    } 
    
    
    if (%time) {   # If specific time has been specified
	if (!$relative) {   # Figure out before, after, or around a time
	    $output .= "around ";
	} elsif ($relative eq 'after') {
	    $output .= "after ";
	} elsif ($relative eq 'before') {
	    $output .= "before ";
	}
	
	# Hour, minute, am/pm
	$hour = $time{'hour'};
	$minute = $time{'minute'};
	$xm = $time{'xm'};

	# Do the output
	$output .= $hour;
	$output .= ":$minute " if ($minute);
	$output .= "$xm " if ($xm);
    } elsif (%departure_time || %arrival_time) {  
        # No specific time, but we do have a day of the week
	
    	if ($departure_time{'weekday'}) {
	    $output .= "on $departure_time{weekday} ";
	} else {
	    $output .= "today ";
	}
	
	if ($departure_time{'time_of_day'}) { 
	    $output .= "in the $departure_time{'time_of_day'} ";
	}
    } else { # If no time given, assume the next flight.
	$output .= "on the next flight ";
    }
	    
    $output =~ s/\s*$//;     # Get rid of trailing spaces

    $output .= ".\n";
}

# Build the new history from the current frame
$history = SpeechBuilder::unparse (%frame);  

if ($error) {   # Something went wrong (but still preserve the history)
  SpeechBuilder::output($error, $history);
} else {
  SpeechBuilder::output($output, $history);
}

open LOG, ">> $LOGFILE";
print LOG localtime().": SEND \"$output\"\n";
close LOG;
