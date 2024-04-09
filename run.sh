#!/bin/bash


# Background processes, one tracks the system status, the other tracks the screen status
python3 system_tracker.py &
# python3 schedule_analysis.py &
python3 screen_tracker.py &

# run the search app
python3 search_app.py