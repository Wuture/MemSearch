# This shell script runs screen_track.py and search_app.py


# Run screen_tracker.py as background process
python3 screen_tracker.py &

python3 search_app.py
