import os
import time
import logging
import socket
import psutil
from pynput import mouse, keyboard
from datetime import datetime
import pyautogui

# Global flag to stop the tracker
tracking_active = True
last_active_time = datetime.now()
user_active = False
internet_status = "Unknown"
screenshot_dir = "C:\\screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

# Function to log mouse movement and clicks
def on_move(x, y):
    global last_active_time, user_active
    last_active_time = datetime.now()
    user_active = True
    log_message(f'Mouse moved to ({x}, {y})')

def on_click(x, y, button, pressed):
    global last_active_time, user_active
    last_active_time = datetime.now()
    user_active = True
    button_name = 'Right' if button == mouse.Button.right else 'Left'
    if pressed:
        log_message(f'Mouse {button_name} button pressed at ({x}, {y})')
    else:
        log_message(f'Mouse {button_name} button released at ({x}, {y})')

# Function to log keyboard activity
def on_press(key):
    global last_active_time, user_active
    last_active_time = datetime.now()
    user_active = True
    try:
        log_message(f'Key {key.char} pressed')
    except AttributeError:
        log_message(f'Special Key {key} pressed')

def on_release(key):
    if key == keyboard.Key.esc:
        return False

# Function to take a screenshot and log it
def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    screenshot_path = os.path.join(screenshot_dir, f'screenshot_{screenshot_time}.png')
    screenshot.save(screenshot_path)
    log_message(f'Screenshot taken and saved to {screenshot_path}')
    # Simulate screenshot upload
    upload_screenshot(screenshot_path)

# Simulate function to upload screenshot and log the upload
def upload_screenshot(screenshot_path):
    # Here you would typically upload the screenshot to a server or cloud
    # For now, we'll just simulate the upload with a log message
    log_message(f'Screenshot uploaded from {screenshot_path}')

# Function to check if the user is active
def check_user_activity():
    global user_active
    if (datetime.now() - last_active_time).seconds > 300:
        if user_active:
            log_message('User is inactive')
            user_active = False
    else:
        if not user_active:
            log_message('User is active')
            user_active = True

# Function to check internet connection status
def check_internet_connection():
    global internet_status
    try:
        socket.create_connection(("www.google.com", 80))
        if internet_status != "Online":
            internet_status = "Online"
            log_message('Internet connection is online')
    except OSError:
        if internet_status != "Offline":
            internet_status = "Offline"
            log_message('Internet connection is offline')

# Function to check if specific applications are running
def check_running_apps():
    monitored_apps = ['chrome.exe', 'whatsapp.exe']  # Add the names of the processes you want to monitor
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in monitored_apps:
            log_message(f'{proc.info["name"]} is running')

# Function to start activity tracker
def start_activity_tracker(log_callback=None):
    global log_message, tracking_active, last_active_time, user_active, internet_status

    log_message = log_callback or print

    # Initialize the activity tracking variables
    last_active_time = datetime.now()
    user_active = False
    internet_status = "Unknown"

    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
    mouse_listener.start()

    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    try:
        while tracking_active:
            take_screenshot()
            check_user_activity()
            check_internet_connection()
            check_running_apps()
            time.sleep(60)
    except KeyboardInterrupt:
        log_message("Activity tracker stopped by user")
    finally:
        mouse_listener.stop()
        keyboard_listener.stop()

# Function to stop activity tracker
def stop_activity_tracker():
    global tracking_active
    tracking_active = False
