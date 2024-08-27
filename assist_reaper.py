import os
import psutil
import sqlite3
from datetime import datetime, timedelta
import time
import librosa
import numpy as np
import pyautogui
import reapy
import pyaudio
import cv2
import openai
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread
from dotenv import load_dotenv

load_dotenv()

# Securely retrieve the OpenAI API Key from an environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# GUI Setup
root = tk.Tk()
root.title("AI Assistant")

# Status Label
status_label = tk.Label(root, text="AI Assistant: OFF", fg="red", font=("Helvetica", 14))
status_label.pack(pady=10)

# Input and Output Display
dialog_frame = tk.Frame(root)
dialog_frame.pack(pady=10)

input_label = tk.Label(dialog_frame, text="Input:")
input_label.grid(row=0, column=0, sticky="w")

input_entry = tk.Entry(dialog_frame, width=50)
input_entry.grid(row=0, column=1)

output_label = tk.Label(dialog_frame, text="Output:")
output_label.grid(row=1, column=0, sticky="w")

output_display = scrolledtext.ScrolledText(dialog_frame, width=50, height=10, wrap=tk.WORD)
output_display.grid(row=1, column=1)

# State Check Display
state_frame = tk.Frame(root)
state_frame.pack(pady=10)

vision_label = tk.Label(state_frame, text="Vision: Not Checked", font=("Helvetica", 12))
vision_label.grid(row=0, column=0, sticky="w")

hearing_label = tk.Label(state_frame, text="Hearing: Not Checked", font=("Helvetica", 12))
hearing_label.grid(row=1, column=0, sticky="w")

context_label = tk.Label(state_frame, text="Context: Not Checked", font=("Helvetica", 12))
context_label.grid(row=2, column=0, sticky="w")

# Function to update state labels
def update_state(vision, hearing, context):
    vision_label.config(text=f"Vision: {vision}")
    hearing_label.config(text=f"Hearing: {hearing}")
    context_label.config(text=f"Context: {context}")

# Function to get AI response from OpenAI API
def get_ai_response(prompt, context):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an assistant specialized in audio and music production."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {prompt}"}
            ]
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error occurred while getting AI response: {e}")
        return "Sorry, I couldn't process your request."

# Function to handle user input and update the dialog
def handle_input(event=None):
    user_input = input_entry.get()
    if user_input.lower() == "exit":
        root.quit()

    recent_activities = get_recent_activities()
    context = "Recent activities: " + ", ".join([f"{act[1]} (details: {act[2]}, audio: {act[3]})" for act in recent_activities])

    response = get_ai_response(user_input, context)
    output_display.insert(tk.END, f"You: {user_input}\n")
    output_display.insert(tk.END, f"Assistant: {response}\n\n")
    output_display.see(tk.END)

    input_entry.delete(0, tk.END)

# Bind the Enter key to the handle_input function
input_entry.bind("<Return>", handle_input)

# Enhanced logging function
def log_activity(activity, details=None, audio_features=None, weight=1.0):
    try:
        conn = sqlite3.connect('activity_log.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS activities
                     (timestamp text, activity text, details text, audio_features text, weight real)''')
        c.execute("INSERT INTO activities VALUES (?,?,?,?,?)", 
                  (datetime.now().isoformat(), activity, str(details), str(audio_features), weight))
        conn.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")
    finally:
        conn.close()

# Function to get recent activities
def get_recent_activities(n=5):
    try:
        conn = sqlite3.connect('activity_log.db')
        c = conn.cursor()
        c.execute("SELECT * FROM activities ORDER BY timestamp DESC, weight DESC LIMIT ?", (n,))
        activities = c.fetchall()
        return activities
    except Exception as e:
        print(f"Error retrieving recent activities: {e}")
        return []
    finally:
        conn.close()

# Function to delete old logs
def delete_old_logs(hours=4):
    try:
        conn = sqlite3.connect('activity_log.db')
        c = conn.cursor()
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        c.execute("DELETE FROM activities WHERE timestamp < ?", (cutoff_time,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting old logs: {e}")
    finally:
        conn.close()

# Function to analyze audio from file
def analyze_audio(audio_file):
    try:
        y, sr = librosa.load(audio_file)
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        return {
            "spectral_centroid": np.mean(spectral_centroid),
            "spectral_rolloff": np.mean(spectral_rolloff)
        }
    except Exception as e:
        print(f"Error analyzing audio file: {e}")
        return {}

# Function to analyze real-time audio stream
def analyze_audio_stream():
    CHUNK = 1024
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 44100

    try:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        
        data = np.frombuffer(stream.read(CHUNK), dtype=np.float32)
        
        spectral_centroid = librosa.feature.spectral_centroid(y=data, sr=RATE)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=data, sr=RATE)
        
        return {
            "spectral_centroid": np.mean(spectral_centroid),
            "spectral_rolloff": np.mean(spectral_rolloff)
        }
    except Exception as e:
        print(f"Error in audio stream analysis: {e}")
        return {}
    finally:
        try:
            stream.stop_stream()
            stream.close()
            p.terminate()
        except Exception as e:
            print(f"Error closing audio stream: {e}")

# Function to get Reaper-specific details using reapy
def get_reaper_context():
    try:
        project = reapy.Project()
        tracks = project.tracks
        current_track = project.selected_track
        effects = current_track.fx

        context = {
            "project_name": project.name,
            "current_track": current_track.name,
            "track_volume": current_track.volume,
            "active_effects": [fx.name for fx in effects],
            "effect_parameters": {fx.name: fx.params for fx in effects},
            "playhead_position": project.cursor_position
        }
        return context
    except Exception as e:
        print(f"Error retrieving Reaper context: {e}")
        return {}

# Function to analyze and capture screen
def analyze_screen():
    try:
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Perform image analysis (e.g., detect shapes, colors, positions)
        
        return {"screen_analysis": "Results of image analysis"}
    except Exception as e:
        print(f"Error capturing or analyzing screen: {e}")
        return {}

# Function to get the active window's title (assuming a utility function)
def get_active_window():
    # Placeholder function; replace with actual implementation
    return "Active Window Title"

# Monitoring function to log activities and update the assistant's status
def monitor():
    global last_log_time
    current_time = time.time()

    if current_time - last_log_time >= log_interval:
        current_window = get_active_window()
        
        if "Reaper" in current_window:
            reaper_context = get_reaper_context()
            audio_features = analyze_audio_stream()
            screen_analysis = analyze_screen()
            full_context = {**reaper_context, **audio_features, **screen_analysis}
            log_activity("Reaper", reaper_context, audio_features, weight=1.5)
            update_state("OK", "OK", "OK")
        else:
            log_activity(current_window)
            update_state("Not OK", "Not OK", "Not OK")
        
        last_log_time = current_time

    delete_old_logs()

    # Update status label
    status_label.config(text="AI Assistant: ON", fg="green")

    # Schedule the next call
    root.after(1000, monitor)

# Initialize log time and interval
last_log_time = time.time()
log_interval = 5  # Log every 5 seconds

# Start monitoring
monitor_thread = Thread(target=monitor)
monitor_thread.start()

# Start the GUI loop
root.mainloop()
