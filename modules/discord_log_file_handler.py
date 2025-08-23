import os, wave, time

import pyaudio

class DiscordLogFileHandler():
    def __init__(self, log_file_path, OUTPUT_DEVICE_NAME, SOUND_FILE):
        super().__init__()
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

        # Check if sound file exists
        if os.path.exists(self.SOUND_FILE):
            print(f"Sound file found: {self.SOUND_FILE}")
        else:
            print(f"Sound file not found: {self.SOUND_FILE}")

        self.follow(log_file_path)

    def follow(self, file_path, sleep_sec=0.5):
        """
        Mimics `tail -f` while handling log rotation.
        """
        with open(file_path, "r") as f:
            # Go to the end of the file
            f.seek(0, os.SEEK_END)
            inode = os.fstat(f.fileno()).st_ino

            while True:
                line = f.readline()
                if line:
                    if "Connection state change: CONNECTING => CONNECTED" in line:
                        print(f"Playing {self.SOUND_FILE}", end="")
                        self.play_sound()
                else:
                    # Check if the file has been rotated
                    try:
                        new_inode = os.stat(file_path).st_ino
                    except FileNotFoundError:
                        new_inode = None

                    if new_inode != inode:
                        try:
                            # Reopen the file
                            f.close()
                            f = open(file_path, "r")
                            inode = os.fstat(f.fileno()).st_ino
                            print(f"\n--- Log rotated, reopened {file_path} ---\n")
                        except FileNotFoundError:
                            # File doesn’t exist yet, wait until recreated
                            time.sleep(sleep_sec)
                            continue
                    else:
                        time.sleep(sleep_sec)

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