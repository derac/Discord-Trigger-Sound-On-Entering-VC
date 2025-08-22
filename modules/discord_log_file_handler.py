import os, wave

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pyaudio

class DiscordLogFileHandler(FileSystemEventHandler):
    def __init__(self, log_file_path, OUTPUT_DEVICE_NAME, SOUND_FILE):
        super().__init__()
        self.log_file_path = os.path.abspath(log_file_path)
        self.file_handle = None
        self.last_position = 0
        self.audio = pyaudio.PyAudio()
        self.OUTPUT_DEVICE_NAME = OUTPUT_DEVICE_NAME
        self.SOUND_FILE = SOUND_FILE
        
        # Choose output device on init
        self.output_device_index = self.find_output_device()
        if self.output_device_index is not None:
            device_info = self.audio.get_device_info_by_index(self.output_device_index)
            print(f"✅ Using output device: {device_info['name']} (Index: {self.output_device_index})")
        else:
            print(f"❌ No suitable output device found for '{self.OUTPUT_DEVICE_NAME}'")
            print("Available output devices:")
            self.list_available_devices()
        
        self._open_log_file()
        
        # Check if sound file exists
        if os.path.exists(self.SOUND_FILE):
            print(f"Sound file found: {self.SOUND_FILE}")
        else:
            print(f"Sound file not found: {self.SOUND_FILE}")

    def _open_log_file(self):
        if self.file_handle:
            self.file_handle.close()
        try:
            self.file_handle = open(self.log_file_path, 'r', encoding='utf-8', errors='ignore')
            self.file_handle.seek(0, os.SEEK_END)
            self.last_position = self.file_handle.tell()
            print(f"Monitoring log file: {self.log_file_path}")
        except FileNotFoundError:
            print(f"Log file not found: {self.log_file_path}")
            self.file_handle = None
        except Exception as e:
            print(f"Error opening log file: {e}")
            self.file_handle = None

    def on_modified(self, event):
        if os.path.abspath(event.src_path) == self.log_file_path and self.file_handle:
            try:
                current_size = os.path.getsize(self.log_file_path)
                
                if current_size < self.last_position:
                    print("Log file was truncated, reopening...")
                    self._open_log_file()
                    return
                
                if current_size > self.last_position:
                    self.file_handle.seek(self.last_position)
                    new_content = self.file_handle.read()
                    if new_content:
                        lines = new_content.splitlines()
                        for line in lines:
                            if "Connection state change: CONNECTING => CONNECTED" in line:
                                print("Connected to Discord voice channel")
                                self.play_sound()
                    
                    self.last_position = self.file_handle.tell()
                    
            except Exception as e:
                print(f"Error reading log file: {e}")
                self._open_log_file()

    def on_created(self, event):
        if os.path.abspath(event.src_path) == self.log_file_path:
            print(f"Log file created: {event.src_path}. Reopening...")
            self._open_log_file()

    def on_deleted(self, event):
        if os.path.abspath(event.src_path) == self.log_file_path:
            print(f"Log file deleted: {event.src_path}. Waiting for new file...")
            if self.file_handle:
                self.file_handle.close()
                self.file_handle = None

    def list_available_devices(self):
        """List all available audio output devices"""
        device_count = self.audio.get_device_count()
        for i in range(device_count):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxOutputChannels'] > 0:
                print(f"  {i}: {device_info['name']}")

    def find_output_device(self):
        """Find the configured output device"""
        device_count = self.audio.get_device_count()
        
        print(f"🔍 Looking for output device: {self.OUTPUT_DEVICE_NAME}")
        
        for i in range(device_count):
            device_info = self.audio.get_device_info_by_index(i)
            if (self.OUTPUT_DEVICE_NAME.lower() in device_info['name'].lower() and 
                device_info['maxOutputChannels'] > 0):
                return i
        
        return None

    def play_sound(self):
        """Play the sound effect through the configured output device"""
        try:
            if not os.path.exists(self.SOUND_FILE):
                print(f"❌ Sound file not found: {self.SOUND_FILE}")
                return
            
            if self.output_device_index is None:
                print("❌ No output device configured")
                return
            
            # Open and play the WAV file
            with wave.open(self.SOUND_FILE, 'rb') as wf:
                channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                sample_rate = wf.getframerate()
                frames = wf.readframes(wf.getnframes())
                
                print(f"🎵 Playing audio: {channels} channels, {sample_width * 8}-bit, {sample_rate} Hz")
                
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(sample_width),
                    channels=channels,
                    rate=sample_rate,
                    input=False,
                    output=True,
                    frames_per_buffer=1024,
                    output_device_index=self.output_device_index
                )
                
                stream.write(frames)
                stream.stop_stream()
                stream.close()
                print("✅ Sound played successfully!")
                
        except Exception as e:
            print(f"❌ Error playing sound: {e}")