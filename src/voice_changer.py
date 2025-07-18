import asyncio
import platform
import numpy as np
import sounddevice as sd
import scipy.signal as signal
from scipy.io import wavfile
import sox
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import time

# Audio settings for WM8960
SAMPLE_RATE = 44100  # Hz, WM8960 supports up to 48kHz
BLOCK_SIZE = 1024    # Samples per block for real-time processing
CHANNELS = 2         # Stereo for WM8960

# Voice effect parameters (initial values)
pitch_shift = -0.3   # Lower pitch for Dark Helmet's deep voice
distortion_gain = 1.5  # Slight distortion for gritty effect
reverb_room_size = 0.5  # Medium reverb for helmet effect
volume = 0.8         # Output volume (0.0 to 1.0)

# Lock for thread-safe parameter updates
param_lock = threading.Lock()

# SoX transformer for effects
tfm = sox.Transformer()

def apply_effects(audio):
    """Apply Dark Helmet voice effects to audio data."""
    global pitch_shift, distortion_gain, reverb_room_size, volume
    with param_lock:
        local_pitch = pitch_shift
        local_distortion = distortion_gain
        local_reverb = reverb_room_size
        local_volume = volume

    # Convert audio to numpy array if not already
    audio = np.array(audio, dtype=np.float32)

    # Save input audio to temporary file
    temp_input = "temp_input.wav"
    temp_output = "temp_output.wav"
    wavfile.write(temp_input, SAMPLE_RATE, audio)

    # Configure SoX effects
    tfm = sox.Transformer()
    tfm.pitch(local_pitch * 12)  # Pitch shift in semitones
    tfm.overdrive(local_distortion)  # Distortion effect
    tfm.reverb(reverb_room_size=reverb_room_size, wet_only=False)  # Reverb
    tfm.vol(local_volume)  # Volume adjustment

    # Process audio
    tfm.build(temp_input, temp_output)
    _, processed_audio = wavfile.read(temp_output)

    # Clean up temporary files
    os.remove(temp_input)
    os.remove(temp_output)

    # Ensure output is stereo and float32
    if processed_audio.ndim == 1:
        processed_audio = np.stack([processed_audio, processed_audio], axis=1)
    processed_audio = processed_audio.astype(np.float32) / 32768.0
    return processed_audio

def audio_callback(indata, outdata, frames, time, status):
    """Real-time audio processing callback."""
    if status:
        print(f"Audio callback status: {status}")
    
    # Apply notch filter to reduce feedback (centered at 1kHz)
    notch_freq = 1000  # Hz
    Q = 30.0  # Quality factor
    b, a = signal.iirnotch(notch_freq / (SAMPLE_RATE / 2), Q)
    filtered_data = signal.lfilter(b, a, indata, axis=0)
    
    # Apply voice effects
    processed = apply_effects(filtered_data)
    
    # Write to output
    outdata[:] = processed[:frames]

# Web server for control interface
class WebInterface(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as f:
                self.wfile.write(f.read())
        elif self.path == "/settings":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            with param_lock:
                settings = {
                    "pitch_shift": pitch_shift,
                    "distortion_gain": distortion_gain,
                    "reverb_room_size": reverb_room_size,
                    "volume": volume
                }
            self.wfile.write(json.dumps(settings).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/settings":
            content_length = int(self.headers["Content-Length"])
            post_data = self.rfile.read(content_length)
            params = json.loads(post_data.decode())
            
            with param_lock:
                global pitch_shift, distortion_gain, reverb_room_size, volume
                pitch_shift = float(params.get("pitch_shift", pitch_shift))
                distortion_gain = float(params.get("distortion_gain", distortion_gain))
                reverb_room_size = float(params.get("reverb_room_size", reverb_room_size))
                volume = float(params.get("volume", volume))
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    """Run the web server."""
    server = HTTPServer(("0.0.0.0", 8000), WebInterface)
    server.serve_forever()

async def main():
    # Start web server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Configure WM8960 audio device
    device = "wm8960-soundcard"
    
    # Start audio stream
    with sd.Stream(device=(device, device),
                   samplerate=SAMPLE_RATE,
                   blocksize=BLOCK_SIZE,
                   channels=CHANNELS,
                   callback=audio_callback,
                   dtype="float32"):
        print("Voice changer running. Access web interface at http://<pi-ip>:8000")
        while True:
            await asyncio.sleep(1)

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())