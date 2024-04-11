# UtopiaOS MemSearch

UtopiaOS MemSearch enhances your MacOS experience by providing a powerful capability to search through your own interaction history. It uses screen tracking and OCR technologies to record and analyze your screen, allowing you to retrieve information seamlessly from past activities.

## Installation
To install the necessary dependencies for UtopiaOS MemSearch, run the following command:

1. Clone the repository
2. Create a virtual environment:
```bash
python -m venv MemSearch
```

3. Activate the virtual environment (MacOS)
```bash
source myenv/bin/activate
```

4. Install the required packages:
```bash
pip install -r requirements.txt
```
Ensure you have Python installed on your system to use pip. It is also recommended to use a virtual environment to manage the dependencies.

## Usage
To start using UtopiaOS MemSearch, execute the included shell script:

```bash
./run.sh
```
This script initializes the system and starts all necessary services for tracking and searching your OS interaction history.

By default, we will search through the entire screen. If you want to search through active windows, provide argument for the search_app.py, by typing "active" in prompt. To start the MemSearch Python app, simply type:

```bash
python3 search_app.py
```

To search, just type in any keyword:
![General Search](examples/general.png)

To do app search, please type in name of the app, follow by ": ", and then keyword. e.g. "Arc: No country for old man". 
![App Search](examples/app%20search.png)


## Components
UtopiaOS MemSearch consists of several Python scripts, each serving a unique role in the system:

1. screen_tracker.py: This script records your screen activity and performs OCR (Optical Character Recognition) to extract key textual information from the screen.

2. search_app.py: A Python application with a simple GUI that allows you to search through your MacOS interaction history.

3. search.py: Contains the search functions used by the application to identify keywords and retrieve relevant results from your OS history.

4. active_window.py: Focuses on capturing screenshots of the active window rather than the entire screen. Note: This script currently has bugs and is pending fixes.

5. system_tracker.py: Tracks all open applications, marking each as active or dormant, thus providing a comprehensive view of your system's application usage over time.

6. analyze_usage_behavior.py: Analyze user software usage on their computers.

7. schedule_analysis.py: Schedule software usage analysis every day. 

8. daily_summary.py: generate an AI report of user's usage today. User could proceed to ask questions about his daily routines. 
