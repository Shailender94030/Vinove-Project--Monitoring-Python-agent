import time
import boto3
from PIL import ImageGrab
from pynput import mouse, keyboard
from datetime import datetime
import io
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import os
import subprocess
import threading
import psutil
import pyautogui
import concurrent.futures

# Load environment variables from .env file
load_dotenv()

# AWS S3 Configuration
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
SS_TIME = int(os.getenv('SS_TIME', 300))  # Default to 300 seconds if not set

# Initialize the S3 client
s3_client = boto3.client('s3',
                         region_name=AWS_REGION,
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# Global variables
current_timezone_cache = None
monitoring_active = False
last_active_time = datetime.now()
user_active = False
internet_status = "Unknown"
screenshot_dir = "C:\\screenshots"
os.makedirs(screenshot_dir, exist_ok=True)

def log_activity(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gui.activity_log.insert(tk.END, f"[{timestamp}] {message}\n")
    gui.activity_log.yview(tk.END)

def get_current_timezone():
    try:
        result = subprocess.run(['tzutil', '/g'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log_activity(f"Error retrieving timezone: {e}")
        return None

def detect_timezone_change():
    global current_timezone_cache
    previous_timezone = get_current_timezone()
    current_timezone_cache = previous_timezone
    log_activity(f"Initial Timezone: {previous_timezone}")

    while monitoring_active:
        time.sleep(60)  # Increased sleep time for reduced CPU usage
        current_timezone = get_current_timezone()
        if current_timezone != current_timezone_cache:
            log_activity(f"Timezone changed from {current_timezone_cache} to {current_timezone}")
            show_popup(f"Timezone changed from {current_timezone_cache} to {current_timezone}")
            current_timezone_cache = current_timezone

def show_popup(message):
    messagebox.showerror("Notification", message)

def take_screenshot_and_upload():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"screenshot{timestamp}.png"
    image = ImageGrab.grab()
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(s3_client.upload_fileobj, buffer, S3_BUCKET_NAME, filename)
    
    log_activity(f"Uploaded {filename} to S3 bucket {S3_BUCKET_NAME}")

def download_screenshot():
    save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
    if save_path:
        image = ImageGrab.grab()
        image.save(save_path)
        log_activity(f"Screenshot saved at {save_path}")

def on_move(x, y):
    update_activity()

def on_click(x, y, button, pressed):
    update_activity()
    button_name = 'Right' if button == mouse.Button.right else 'Left'
    action = 'pressed' if pressed else 'released'
    log_activity(f'Mouse {button_name} button {action} at ({x}, {y})')

def on_press(key):
    update_activity()
    try:
        log_activity(f'Key {key.char} pressed')
    except AttributeError:
        log_activity(f'Special Key {key} pressed')

def update_activity():
    global last_active_time, user_active
    last_active_time = datetime.now()
    user_active = True

def check_user_activity():
    global user_active
    if (datetime.now() - last_active_time).seconds > 300:
        if user_active:
            log_activity('User is inactive')
            user_active = False
    else:
        if not user_active:
            log_activity('User is active')
            user_active = True

def check_running_apps():
    monitored_apps = ['chrome.exe', 'whatsapp.exe']
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in monitored_apps:
            log_activity(f'{proc.info["name"]} is running')

def setup_mouse_listener():
    listener = mouse.Listener(on_move=on_move, on_click=on_click)
    listener.start()
    return listener

def setup_keyboard_listener():
    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()

def start_monitoring():
    global monitoring_active
    monitoring_active = True
    threading.Thread(target=monitoring_loop, daemon=True).start()
    threading.Thread(target=start_activity_tracker, daemon=True).start()

def stop_monitoring():
    global monitoring_active
    monitoring_active = False
    log_activity("Monitoring stopped")

def monitoring_loop():
    while monitoring_active:
        detect_timezone_change()
        take_screenshot_and_upload()
        time.sleep(SS_TIME)

def start_activity_tracker():
    global last_active_time
    setup_mouse_listener()
    setup_keyboard_listener()

    while monitoring_active:
        check_user_activity()
        check_running_apps()
        time.sleep(5)

class AgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Agent GUI")
        self.root.geometry("1200x600")  # Set window size

        self.label = tk.Label(root, text="Agent GUI with Additional Features", font=("Arial", 16))
        self.label.pack(pady=10)

        self.activity_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, width=100)
        self.activity_log.pack(pady=10)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(self.button_frame, text="Start Monitoring", command=start_monitoring)
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(self.button_frame, text="Stop Monitoring", command=stop_monitoring)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.download_button = tk.Button(self.button_frame, text="Download Screenshot", command=download_screenshot)
        self.download_button.grid(row=0, column=2, padx=5)

        self.screenshot_button = tk.Button(self.button_frame, text="Take Screenshot", command=take_screenshot_and_upload)
        self.screenshot_button.grid(row=0, column=3, padx=5)

def main():
    global gui
    root = tk.Tk()
    gui = AgentGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
