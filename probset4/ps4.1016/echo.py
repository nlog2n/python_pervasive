#!/usr/bin/python2.3

import galaxy.server
 
server1 = galaxy.server.Server("soccf-smasrv01.ddns.comp.nus.edu.sg", 12647, "g0404400")
server1.connect()  # Actually connect to the Galaxy frame relay

# Use the active variable to quit if we get a goodbye
active = 1
while (active):
    # Look for an incoming message from the server
    c = server1.handleMessage(0)

    # If we got a message (recognition result)
    if c:

        # Print out the frame
        print c.frame.toString()
        # Figure out the action
        action = c.frame.getAction()
        mytext = c.frame.getText()

        
        if (action == 'call_answered'): # The call_answered action means we just got a new connection
            c.sb_reply('Welcome to map quest system')
        
        elif (action == 'good_bye'): # Good bye means close off the conversation
            c.sb_goodbye('Good Bye')
            active = 0
            
        elif (action == 'take') :
            c.sb_reply('take take take')
            
        elif (action == 'where') :
            c.sb_reply('where where where')
        
        elif (action): # This means we really got some stuff
        
            if mytext:
                c.sb_reply('Repeat '+ mytext)
            else:
                c.sb_reply('Do not know')
        else:
            # This shouldn't happen
            c.sb_reply('What did you say')
