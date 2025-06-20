#!/bin/bash
# Run the VLC Python script as vlcuser
su - vlcuser -c "python3 /home/vlcuser/vlc.py -t $1"
