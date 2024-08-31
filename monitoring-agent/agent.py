import os
import time
import socket
import psutil
from pynput import mouse, keyboard
from datetime import datetime
import pyautogui
import boto3
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog, simpledialog
import threading
import queue
import subprocess
import webbrowser
import random

# Load environment variables from .env file
load_dotenv()

# AWS S3 Configuration
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
SS_TIME = int(os.getenv('SS_TIME', '300'))  # Default to 5 minutes if not set

# Initialize the S3 client
s3_client = boto3.client('s3',
                         region_name=AWS_REGION,
                         aws_access_key_id=AWS_ACCESS_KEY_ID,
                         aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

# Global variables for tracking
tracking_active = False
last_active_time = datetime.now()
user_active = False
screenshot_dir = "C:\\screenshots"
os.makedirs(screenshot_dir, exist_ok=True)
current_timezone_cache = None
log_queue = queue.Queue()
ss_time_lock = threading.Lock()
mouse_listener = None
keyboard_listener = None
ss_time = SS_TIME  # Initialize with the default or loaded value

# CAPTCHA setup
CAPTCHA_WORDS = ["cat", "dog", "fish", "bird", "bat"]
CAPTCHA_ATTEMPTS = 3

def jumble_word(word):
    return ''.join(random.sample(word, len(word)))

def verify_captcha(user_input, correct_word):
    return user_input.strip().lower() == correct_word

def update_captcha(captcha_label):
    global correct_word, jumbled_word
    correct_word = random.choice(CAPTCHA_WORDS)
    jumbled_word = jumble_word(correct_word)
    captcha_label.config(text=f"Unscramble this word: {jumbled_word}")

def show_captcha_window():
    global correct_word, jumbled_word
    correct_word = random.choice(CAPTCHA_WORDS)
    jumbled_word = jumble_word(correct_word)
    attempts_left = CAPTCHA_ATTEMPTS

    def on_submit():
        nonlocal attempts_left
        user_input = captcha_entry.get()
        if verify_captcha(user_input, correct_word):
            captcha_window.destroy()
            main()
        else:
            attempts_left -= 1
            if attempts_left > 0:
                messagebox.showerror("Error", f"Incorrect CAPTCHA. {attempts_left} attempts left.")
                captcha_entry.delete(0, tk.END)
                update_captcha(captcha_label)  # Update CAPTCHA
            else:
                messagebox.showerror("Error", "Too many incorrect attempts. Exiting.")
                captcha_window.destroy()
                exit()

    captcha_window = tk.Tk()
    captcha_window.title("CAPTCHA Verification")

    captcha_label = tk.Label(captcha_window, text=f"Unscramble this word: {jumbled_word}")
    captcha_label.pack(pady=10)

    captcha_entry = tk.Entry(captcha_window)
    captcha_entry.pack(pady=10)

    submit_button = tk.Button(captcha_window, text="Submit", command=on_submit)
    submit_button.pack(pady=10)

    captcha_window.mainloop()

def log_activity(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_queue.put(f"[{timestamp}] {message}")

def update_log(gui):
    while not log_queue.empty():
        message = log_queue.get()
        gui.activity_log.insert(tk.END, message + "\n")
        gui.activity_log.yview(tk.END)
    gui.root.after(100, update_log, gui)

def get_current_timezone():
    try:
        result = subprocess.run(['tzutil', '/g'], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        log_activity(f"Error retrieving timezone: {e}")
        return None

def detect_timezone_change(interval=10):
    global current_timezone_cache
    previous_timezone = get_current_timezone()
    current_timezone_cache = previous_timezone
    log_activity(f"Initial Timezone: {previous_timezone}")

    while tracking_active:
        time.sleep(interval)
        current_timezone = get_current_timezone()
        if current_timezone != current_timezone_cache:
            log_activity(f"Timezone changed from {current_timezone_cache} to {current_timezone}")
            show_popup(f"Timezone changed from {current_timezone_cache} to {current_timezone}")
            current_timezone_cache = current_timezone

def check_internet_connection():
    try:
        socket.create_connection(("www.google.com", 80), timeout=2)
        return "Online"
    except OSError:
        return "Offline"

def show_popup(message):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showinfo("Notification", message)
    root.destroy()

def take_screenshot_and_upload():
    try:
        screenshot = pyautogui.screenshot()
        screenshot_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        screenshot_path = os.path.join(screenshot_dir, f'screenshot_{screenshot_time}.png')
        screenshot.save(screenshot_path)
        log_activity(f'Screenshot taken and saved to {screenshot_path}')

        # Upload to S3
        with open(screenshot_path, 'rb') as f:
            s3_client.upload_fileobj(f, S3_BUCKET_NAME, f'screenshots/{os.path.basename(screenshot_path)}')
            log_activity(f"Uploaded {screenshot_path} to S3 bucket {S3_BUCKET_NAME}")
    except Exception as e:
        log_activity(f"Error taking screenshot or uploading: {e}")

def download_screenshot():
    save_path = filedialog.asksaveasfilename(defaultextension=".png",
                                             filetypes=[("PNG files", ".png"), ("All files", ".*")])
    if save_path:
        screenshot = pyautogui.screenshot()
        screenshot.save(save_path)
        log_activity(f'Screenshot saved to {save_path}')
        show_popup(f'Screenshot saved to {save_path}')

def set_interval_time(gui):
    global ss_time
    interval = simpledialog.askinteger("Set Interval", "Enter interval time in seconds:", minvalue=1)
    if interval:
        with ss_time_lock:
            ss_time = interval
        log_activity(f"Screenshot interval time set to {ss_time} seconds")
        show_popup(f"Screenshot interval time set to {ss_time} seconds")

def on_move(x, y):
    global last_active_time, user_active
    last_active_time = datetime.now()
    user_active = True

def on_click(x, y, button, pressed):
    global last_active_time, user_active
    last_active_time = datetime.now()
    user_active = True
    button_name = 'Right' if button == mouse.Button.right else 'Left'
    log_activity(f'Mouse {button_name} button {"pressed" if pressed else "released"} at ({x}, {y})')

def on_press(key):
    global last_active_time, user_active
    last_active_time = datetime.now()
    user_active = True
    try:
        log_activity(f'Key {key.char} pressed')
    except AttributeError:
        log_activity(f'Special Key {key} pressed')

def check_user_activity(gui):
    global user_active
    if (datetime.now() - last_active_time).seconds > 300:
        if user_active:
            log_activity('User is inactive')
            gui.user_status_label.config(text="User Status: Inactive")
            user_active = False
    else:
        if not user_active:
            log_activity('User is active')
            gui.user_status_label.config(text="User Status: Active")
            user_active = True

def check_running_apps():
    monitored_apps = ['chrome.exe', 'whatsapp.exe']
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in monitored_apps:
            log_activity(f'{proc.info["name"]} is running')

def periodic_tasks(gui):
    if not tracking_active:
        return
    check_user_activity(gui)
    internet_status = check_internet_connection()
    log_activity(f"Internet Status: {internet_status}")
    check_running_apps()
    gui.root.after(60000, periodic_tasks, gui)

def start_activity_tracker():
    global mouse_listener, keyboard_listener
    mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
    keyboard_listener = keyboard.Listener(on_press=on_press)

    mouse_listener.start()
    keyboard_listener.start()

    while tracking_active:
        take_screenshot_and_upload()
        with ss_time_lock:
            time.sleep(ss_time)

def start_monitoring(gui):
    global tracking_active
    tracking_active = True
    log_activity("Monitoring started")
    threading.Thread(target=start_activity_tracker, daemon=True).start()
    threading.Thread(target=detect_timezone_change, daemon=True).start()
    periodic_tasks(gui)

def stop_monitoring():
    global tracking_active
    tracking_active = False

    if mouse_listener:
        mouse_listener.stop()
    if keyboard_listener:
        keyboard_listener.stop()

    log_activity("Monitoring stopped")

def open_s3_bucket():
    bucket_url = f"https://eu-north-1.console.aws.amazon.com/s3/buckets/{S3_BUCKET_NAME}?region=eu-north-1"
    webbrowser.open(bucket_url)

class AgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Agent GUI with Additional Features")
        self.root.geometry("1200x600")

        self.label = tk.Label(root, text="Agent GUI with Additional Features", font=("Arial", 16))
        self.label.pack(pady=10)

        self.activity_log = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=20, width=100)
        self.activity_log.pack(pady=10)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack(pady=10)

        self.start_button = tk.Button(self.button_frame, text="Start Monitoring", command=lambda: start_monitoring(self))
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(self.button_frame, text="Stop Monitoring", command=stop_monitoring)
        self.stop_button.grid(row=0, column=1, padx=5)

        self.download_button = tk.Button(self.button_frame, text="Download Screenshot", command=download_screenshot)
        self.download_button.grid(row=0, column=2, padx=5)

        self.check_internet_button = tk.Button(self.button_frame, text="Check Internet Connection", 
            command=self.check_internet_status)
        self.check_internet_button.grid(row=0, column=3, padx=5)

        self.set_interval_button = tk.Button(self.button_frame, text="Set Interval Time", command=lambda: set_interval_time(self))
        self.set_interval_button.grid(row=0, column=4, padx=5)

        self.open_s3_button = tk.Button(self.button_frame, text="Open S3 Bucket", command=open_s3_bucket)
        self.open_s3_button.grid(row=0, column=5, padx=5)

        self.exit_button = tk.Button(self.button_frame, text="Exit", command=self.root.quit)
        self.exit_button.grid(row=0, column=6, padx=5)

        self.user_status_label = tk.Label(root, text="User Status: Unknown", font=("Arial", 12))
        self.user_status_label.pack(pady=10)

        # Start updating log
        update_log(self)

    def check_internet_status(self):
        status = check_internet_connection()
        show_popup(f"Internet Status: {status}")

def main():
    root = tk.Tk()
    gui = AgentGUI(root)
    root.mainloop()

if __name__ == "__main__":
    show_captcha_window()
