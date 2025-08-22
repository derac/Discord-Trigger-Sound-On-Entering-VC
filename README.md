# Discord Voice Channel Sound Trigger

Plays a sound effect when you join a Discord voice channel.

## What it does

This script monitors Discord's log files and automatically plays a sound effect (`sound_to_play.wav`) when you connect to a voice channel.

## Setup

1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```

## Customization

You can easily customize the script by editing the configuration section at the top of `main.py`:

```python
# Configuration - easily change these values
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_FILE = os.path.join(SCRIPT_DIR, "sound_to_play.wav")  # Change to your sound file
OUTPUT_DEVICE_NAME = "CABLE In 16ch"  # Change to your audio device
```

**Sound File Options:**
- Replace `sound_to_play.wav` with any WAV file you prefer
- The script automatically finds the file relative to the script location
- WAV format is recommended for best compatibility

**Audio Device Options:**
- Change `OUTPUT_DEVICE_NAME` to match your system's audio devices
- The script will show all available devices if it can't find the configured one

## Usage

Run the script:
```bash
python main.py
```

The script will:
- Automatically detect your OS and find Discord's log directory
- Show which audio device it's using
- Monitor for voice channel connections
- Play the sound when you join a voice channel

Press `Ctrl+C` to stop.

## Requirements

- Python 3.6+
- Discord desktop app
- Audio output device
- Sound file (WAV format required)

## VB-Audio Virtual Cable Setup (Optional)

If you want to route the sound to other applications (like Discord itself), you'll need VB-Audio Virtual Cable:

1. **Download VB-Audio Virtual Cable:**
   - Go to [VB-Audio Virtual Cable](https://vb-audio.com/Cable/)
   - Download the free version for your OS

2. **Install:**
   - Run the installer as administrator
   - Restart your computer after installation

3. **Configure in Script:**
   - If you need to, change `OUTPUT_DEVICE_NAME = "CABLE In 16ch"` in `main.py`
   - The script will automatically detect and use the virtual device

4. **Audio Routing:**
   - Set Discord's input device to "CABLE Output (VB-Audio Virtual Cable)"
   - Now the sound will play through Discord to other users in the voice channel

**Note:** VB-Audio Virtual Cable creates a virtual audio cable that allows audio to flow between applications. This is useful if you want the sound effect to be heard by other Discord users.

## Supported Platforms

- Windows
- Linux  
- macOS