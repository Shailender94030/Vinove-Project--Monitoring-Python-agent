# Project Name: Activity Tracker with Agent-Based Monitoring

*Overview:-
This project is designed to distinguish between genuine user activity and bot activity using only a keyboard, monitor, and mouse. The system is designed to track user activities in real-time and manage the application lifecycle effectively.

## GUI OVERVIEW:-

### Captcha Page:-
![Screenshot (361)](https://github.com/user-attachments/assets/7050ace0-009a-40d1-9f94-d5f158193eb8)

### Main Gui Page:-

![Screenshot (362)](https://github.com/user-attachments/assets/3517eac2-40f7-41e3-895e-2f948415ec96)

### Internet Connectivity:-

##### Online
![Screenshot (363)](https://github.com/user-attachments/assets/8d4c5e25-bd61-482b-b169-f47ea4f68ff6)
#### Offline

![Screenshot (365)](https://github.com/user-attachments/assets/c8dec37f-402b-40ce-b6d3-812367932a13)

### Activity Tracking Preview:-

![Screenshot (364)](https://github.com/user-attachments/assets/f6693dde-f5d9-4873-a7bd-567f23394e2b)

## AWS Preview:-

![Screenshot (357)](https://github.com/user-attachments/assets/97f4e3d3-0050-4915-b689-1f90e53f9192)

![Screenshot (358)](https://github.com/user-attachments/assets/19f304c8-b520-49b0-ad13-c086c0d47ed2)

![Screenshot (359)](https://github.com/user-attachments/assets/d0d84cfc-eff3-4289-9332-866710004c73)

![screenshot20240829004939](https://github.com/user-attachments/assets/18f43bec-933c-4ae6-9bfc-c43c635dbf15)

.Amazon S3:- For storing and managing uploaded screenshots and activity logs.

.AWS Lambda:- For handling the backend processing of uploads, such as file storage or data transformation.

.AWS IAM:- For managing permissions and roles required for secure interaction with S3 and Lambda.

.Boto3:- AWS SDK for Python to interact with S3 for uploading files.



##### *Directory Structure:-
monitoring-agent
├── .env
├── .gitignore
├── activity_tracker.py
├── agent.py
├── get-screenshots-from-s3.py
└── README.md


## Flow chart:-

![Screenshot (366)](https://github.com/user-attachments/assets/8eb1acd9-2451-45d2-9d3b-19919bae27e4)

##Technologies Used:

*File Descriptions
*`env`:
This file contains environment variables that are necessary for the application. It includes sensitive information like API keys, database URLs, and other configuration settings. Ensure this file is never shared publicly.

*`gitignore`:
Specifies files and directories that should be ignored by Git. This typically includes environment variables, compiled files, and other files that should not be version controlled.

*`activity_tracker.py`:
This script is responsible for tracking the user's activities on the system. It monitors keyboard and mouse inputs and logs them for analysis. The tracking data is crucial for distinguishing between genuine user activities and bot activities.

*`agent.py`:
This script handles the main application logic, including initializing the agent, starting activity tracking, and managing the application lifecycle. The agent interacts with the activity_tracker.py module to get real-time data.

*`get-screenshots-from-s3.py`:
This script is used to retrieve screenshots from an S3 bucket. It is likely part of the monitoring system to capture visual data of the user's activities or the system's state during operation.

"Setup Instructions:"
1. Clone the Repository
bash-code:
>git clone https://github.com/Shailender94030/Vinove-Project--monitoring-python-agent.git

>cd your-repo-name

2. Install Dependencies
Ensure that you have Python installed. Install the required dependencies using `pip`:
bash-code:

>pip install -r requirements.txt

3. Configure Environment Variables
Copy the `.env.example` file to `.env` and update the environment variables as needed:
bash-code

>cp .env.example .env

4. Run the Application
You can start the application by running the following command:

bash-code:

>python main.py

"Usage:"

.The Activity Tracker continuously     monitors user inputs and logs them.

.The Agent manages the overall application, initiating the activity tracking and processing the data.

.The Screenshot Retrieval script can be run separately to fetch screenshots for further analysis.

"Contributing:"
If you want to contribute to this project, please follow these steps:

1.Fork the repository.
2.Create a new branch (`git checkout -b feature-branch`).
3.Make your changes.
4.Commit your changes (`git commit -m 'Add some feature'`).
5.Push to the branch (`git push origin feature-branch`).
6.Open a Pull Request.

## ALL THE MODULE USED IN MAIN FILE i.e., agent.py:-
*Here's a list of all the modules used in your provided code along with a brief explanation for each:

`os`: Provides a way of using operating system-dependent functionality like reading or writing to the file system.

`time`: Provides time-related functions, such as sleep and measuring time intervals.

`socket`: Provides access to the underlying network interface for network communication.

`psutil`: Provides an interface for retrieving information on system utilization (CPU, memory, disks, network, sensors) and running processes.

`pynput`: Allows you to monitor and control input devices (mouse and keyboard) programmatically.

`datetime`: Supplies classes for manipulating dates and times.

`pyautogui`: Provides functions to take screenshots, control the mouse and keyboard, and automate interactions with the GUI.

`boto3`: Amazon Web Services (AWS) SDK for Python, which allows Python developers to write software that makes use of AWS services.

`dotenv`: Loads environment variables from a .env file.

`tkinter`: Provides a GUI toolkit for creating graphical user interfaces in Python.

`subprocess`: Allows spawning new processes, connecting to their input/output/error pipes, and obtaining their return codes.

`webbrowser`: Provides a high-level interface to allow displaying Web-based documents to users.

`random`: Implements pseudo-random number generators for various distributions.

`queue`: Provides a thread-safe queue implementation, useful for inter-thread communication.

`threading`: Provides a way to run tasks concurrently using threads.

*Additional Notes:
`tkinter`: It’s used here to create GUI elements such as windows, labels, buttons, and dialogs.
`pyautogui`: For capturing screenshots and automating GUI interactions.
`boto3`: For interacting with AWS S3 to upload screenshots.
`pynput`: For monitoring keyboard and mouse inputs.

*Installation
 If you don’t have these modules installed, you can install them using pip:

bash-code

"pip install psutil pynput pyautogui boto3 python-dotenv"

.The tkinter module is included with Python’s standard library, so you don't need to install it separately.
