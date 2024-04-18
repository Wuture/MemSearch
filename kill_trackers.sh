#!/bin/bash

# Find and kill the screen_tracker process
screen_tracker_pid=$(pgrep -f "screen_tracker.py")
if [ -n "$screen_tracker_pid" ]; then
    echo "Killing screen_tracker process with PID $screen_tracker_pid"
    kill -9 "$screen_tracker_pid"
else
    echo "screen_tracker process not found"
fi

# Find and kill the system_tracker process
system_tracker_pids=$(pgrep -f "system_tracker.py")
for pid in $system_tracker_pids; do
    echo "Killing system_tracker process with PID $pid"
    kill -9 "$pid"
done
