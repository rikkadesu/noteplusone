import json
import threading

# Data to be autosaved
data = {
    "name": "John",
    "age": 30,
    "city": "New York"
}

# File path for autosave
autosave_file = "autosave_data.json"

# Control variable for autosave and timer
autosave_enabled = True
autosave_timer_enabled = threading.Event()  # Thread-safe event object
autosave_timer_enabled.set()  # Initially, autosave timer is enabled

# Function to perform autosave
def autosave():
    if autosave_enabled:
        with open(autosave_file, "w") as json_file:
            json.dump(data, json_file)
        print("Autosaved data to", autosave_file)

# Timer function for autosave
def autosave_timer():
    # Adjust the interval (in seconds) based on your needs
    autosave_interval = 5  # Save every 5 seconds
    while autosave_timer_enabled.is_set():
        autosave()
        autosave_timer_enabled.wait(autosave_interval)  # Wait for the specified interval

# Function to toggle autosave and timer
def toggle_autosave():
    global autosave_enabled
    autosave_enabled = not autosave_enabled
    status = "enabled" if autosave_enabled else "disabled"
    print(f"Autosave is {status}")
    if autosave_enabled:
        autosave_timer_enabled.set()  # Enable the autosave timer
    else:
        autosave_timer_enabled.clear()  # Disable the autosave timer

# Start the autosave timer thread
autosave_thread = threading.Thread(target=autosave_timer)
autosave_thread.start()

# Example: You can modify 'data' periodically to see it autosaving
# For this example, we'll simulate changes by updating the 'age' field
while True:
    data["age"] += 1
