# UtopiaOS MemSearch

UtopiaOS MemSearch enhances your MacOS experience by providing a powerful capability to search through your own interaction history. It uses screen tracking and OCR technologies to record and analyze your screen, allowing you to retrieve information seamlessly from past activities.

## Installation
To install the necessary dependencies for UtopiaOS MemSearch, run the following command:

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

By default, we will search through the entire screen. If you want to search through active windows, provide argument for the search_app.py, by typing "active" in prompt

```bash
python3 search_app.py
```

## Components
UtopiaOS MemSearch consists of several Python scripts, each serving a unique role in the system:

1. screen_tracker.py: This script records your screen activity and performs OCR (Optical Character Recognition) to extract key textual information from the screen.

2. search_app.py: A Python application with a simple GUI that allows you to search through your MacOS interaction history.

3. search.py: Contains the search functions used by the application to identify keywords and retrieve relevant results from your OS history.

4. search_and_save_pdf.py: This utility allows you to perform searches and compile the results into a PDF document, providing a tangible output for your search queries.

5. active_window_tracker.py: Focuses on capturing screenshots of the active window rather than the entire screen. Note: This script currently has bugs and is pending fixes.

6. system_tracker.py: Tracks all open applications, marking each as active or dormant, thus providing a comprehensive view of your system's application usage over time.

7. analyze_usage_behavior.py: Analyze user software usage on their computers.

8. schedule_analysis.py: Schedule software usage analysis every day. 

9. daily_summary: generate an AI report of user's usage today. User could proceed to ask questions about his daily routines. 