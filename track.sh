#!/bin/bash
# Start the system and screen tracker
python3 trackers/system_tracker.py &
python3 trackers/screen_tracker.py &