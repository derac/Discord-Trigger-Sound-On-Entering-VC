#!/usr/bin/python
import os, time, platform
from watchdog.observers import Observer

from modules.discord_log_file_handler import DiscordLogFileHandler

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE = os.path.join(SCRIPT_DIR, "sound_to_play.wav")
OUTPUT_DEVICE_NAME = "CABLE In 16ch"

def get_discord_logs_directory():
    """Get the Discord logs directory path for the current OS"""
    system = platform.system().lower()
    if system == "windows":
        app_data = os.getenv('APPDATA')
        if app_data:
            return os.path.join(app_data, "discord", "logs")
    elif system == "linux":
        home = os.path.expanduser("~")
        return os.path.join(home, ".config", "discord", "logs")
    elif system == "darwin":
        home = os.path.expanduser("~")
        return os.path.join(home, "Library", "Application Support", "discord", "logs")
    return None



if __name__ == "__main__":
    log_directory = get_discord_logs_directory()
    
    if not log_directory:
        print("❌ Could not determine Discord logs directory for this OS")
        print(f"Current OS: {platform.system()}")
        exit(1)
    
    log_file = "discord-webrtc_0"
    full_log_path = os.path.join(log_directory, log_file)

    print(f"Starting Discord voice channel monitor")
    print(f"Sound file: {SOUND_FILE}")
    print(f"Output device: {OUTPUT_DEVICE_NAME}")
    print(f"OS: {platform.system()}")
    print(f"Log directory: {log_directory}")
    print(f"Log file: {full_log_path}")
    print("Press Ctrl+C to stop")
    
    event_handler = DiscordLogFileHandler(full_log_path, OUTPUT_DEVICE_NAME, SOUND_FILE)
    observer = Observer()
    observer.schedule(event_handler, log_directory, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        observer.stop()
    observer.join()
    print("Monitor stopped.")
