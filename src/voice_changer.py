import asyncio
import platform
import numpy as np
import sounddevice as sd
import scipy.signal as signal
from scipy.io import wavfile
import sox
import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import time

def check_virtual_environment():
    """Check if we're running in the SpaceBalls virtual environment"""
    venv_path = os.environ.get('VIRTUAL_ENV', '')
    if 'SpaceBalls' in venv_path:
        print(f"✓ Running in SpaceBalls virtual environment: {venv_path}")
        return True
    elif venv_path:
        print(f"⚠ Running in different virtual environment: {venv_path}")
        return True
    else:
        print("⚠ WARNING: Not running in a virtual environment!")
        print("  Consider activating the SpaceBalls environment for best results")
        return False

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
    """Real-time audio processing callback with flexible channel handling."""
    if status:
        print(f"Audio callback status: {status}")
    
    try:
        # Handle different input/output channel configurations
        input_data = indata.copy()
        
        # Convert to mono if needed for processing
        if input_data.ndim == 2 and input_data.shape[1] > 1:
            # Mix stereo to mono for processing
            mono_input = np.mean(input_data, axis=1, keepdims=True)
        else:
            mono_input = input_data
        
        # Apply notch filter to reduce feedback (centered at 1kHz)
        notch_freq = 1000  # Hz
        Q = 30.0  # Quality factor
        # Use the actual sample rate from the stream
        current_sample_rate = 44100  # Will be updated in main()
        try:
            b, a = signal.iirnotch(notch_freq / (current_sample_rate / 2), Q)
            filtered_data = signal.lfilter(b, a, mono_input, axis=0)
        except:
            # If filter fails, just use the original data
            filtered_data = mono_input
        
        # Apply voice effects (simplified for real-time processing)
        try:
            processed = apply_effects_realtime(filtered_data)
        except:
            # Fallback: just apply basic volume and pitch
            processed = apply_basic_effects(filtered_data)
        
        # Match output channels to the expected output format
        if outdata.ndim == 2:
            if processed.ndim == 1:
                # Duplicate mono to stereo
                outdata[:, 0] = processed[:frames].flatten()
                if outdata.shape[1] > 1:
                    outdata[:, 1] = processed[:frames].flatten()
            else:
                # Copy processed data, ensuring frame count matches
                outdata[:] = processed[:frames]
        else:
            # Mono output
            outdata[:] = processed[:frames].flatten()
            
    except Exception as e:
        # On any error, just pass through the input with volume reduction
        print(f"Audio processing error: {e}")
        try:
            if outdata.shape == indata.shape:
                outdata[:] = indata * 0.5  # Reduce volume to prevent feedback
            else:
                # Handle shape mismatch
                outdata.fill(0)
        except:
            outdata.fill(0)  # Silence on critical error

def apply_effects_realtime(audio):
    """Apply simplified effects for real-time processing"""
    global pitch_shift, distortion_gain, reverb_room_size, volume
    
    with param_lock:
        local_pitch = pitch_shift
        local_volume = volume
        local_distortion = distortion_gain
    
    # Simple pitch shift using interpolation (faster than SoX)
    if local_pitch != 0:
        try:
            # Simple pitch shift by resampling
            shift_factor = 2 ** (local_pitch)
            new_length = int(len(audio) / shift_factor)
            if new_length > 0:
                indices = np.linspace(0, len(audio) - 1, new_length)
                pitched_audio = np.interp(indices, np.arange(len(audio)), audio.flatten())
                # Pad or trim to original length
                if len(pitched_audio) < len(audio):
                    audio = np.pad(pitched_audio, (0, len(audio) - len(pitched_audio)), mode='constant')
                else:
                    audio = pitched_audio[:len(audio)]
        except:
            pass  # Skip pitch shift on error
    
    # Simple distortion
    if local_distortion > 1.0:
        audio = np.tanh(audio * local_distortion) / local_distortion
    
    # Apply volume
    audio = audio * local_volume
    
    return audio.reshape(-1, 1) if audio.ndim == 1 else audio

def apply_basic_effects(audio):
    """Very basic effects as fallback"""
    global volume
    with param_lock:
        local_volume = volume
    return audio * local_volume

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

def find_suitable_audio_device():
    """Find a suitable audio device with input and output capabilities"""
    try:
        devices = sd.query_devices()
        print("\n🔍 Available audio devices:")
        
        suitable_devices = []
        default_input = sd.default.device[0]
        default_output = sd.default.device[1]
        
        for i, device in enumerate(devices):
            device_info = f"  {i}: {device['name']}"
            if device['max_input_channels'] > 0:
                device_info += f" (IN: {device['max_input_channels']} ch)"
            if device['max_output_channels'] > 0:
                device_info += f" (OUT: {device['max_output_channels']} ch)"
            
            print(device_info)
            
            # Check for WM8960 or USB audio devices
            if ('wm8960' in device['name'].lower() or 
                'usb' in device['name'].lower() or
                'alsa' in device['name'].lower()):
                if (device['max_input_channels'] >= 1 and 
                    device['max_output_channels'] >= 1):
                    suitable_devices.append((i, device))
        
        print(f"\n📱 Default input device: {default_input}")
        print(f"📢 Default output device: {default_output}")
        
        # Try to find the best device
        if suitable_devices:
            device_id, device_info = suitable_devices[0]
            print(f"✅ Selected audio device: {device_info['name']} (ID: {device_id})")
            return device_id, device_info
        else:
            print("⚠️  No specialized audio device found, using system defaults")
            return None, None
            
    except Exception as e:
        print(f"❌ Error querying audio devices: {e}")
        return None, None

def test_audio_configuration(device_id=None, sample_rate=44100, channels=2, blocksize=1024):
    """Test if audio configuration works with the given parameters"""
    try:
        print(f"\n🧪 Testing audio configuration:")
        print(f"   Device: {device_id if device_id else 'Default'}")
        print(f"   Sample rate: {sample_rate}Hz")
        print(f"   Channels: {channels}")
        print(f"   Block size: {blocksize}")
        
        # Test with a very short stream
        with sd.Stream(device=(device_id, device_id) if device_id else None,
                       samplerate=sample_rate,
                       blocksize=blocksize,
                       channels=channels,
                       dtype="float32"):
            pass  # Just test if we can open the stream
        
        print("✅ Audio configuration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Audio configuration test failed: {e}")
        return False

def get_best_audio_config():
    """Find the best working audio configuration"""
    device_id, device_info = find_suitable_audio_device()
    
    # Test different configurations
    configs = [
        # (sample_rate, channels, blocksize)
        (44100, 2, 1024),  # Ideal stereo
        (44100, 1, 1024),  # Mono fallback
        (22050, 2, 512),   # Lower sample rate stereo
        (22050, 1, 512),   # Lower sample rate mono
        (48000, 2, 1024),  # Higher sample rate
        (48000, 1, 1024),  # Higher sample rate mono
    ]
    
    for sample_rate, channels, blocksize in configs:
        print(f"\n🔧 Trying configuration: {sample_rate}Hz, {channels}ch, {blocksize} samples")
        if test_audio_configuration(device_id, sample_rate, channels, blocksize):
            return device_id, sample_rate, channels, blocksize
    
    # If all else fails, try default device with basic config
    print("\n🔄 Trying default device with basic configuration...")
    if test_audio_configuration(None, 22050, 1, 512):
        return None, 22050, 1, 512
    
    raise Exception("No working audio configuration found")
    
    try:
        # Start audio stream
        with sd.Stream(device=(device, device) if device else None,
                       samplerate=SAMPLE_RATE,
                       blocksize=BLOCK_SIZE,
                       channels=CHANNELS,
                       callback=audio_callback,
                       dtype="float32"):
            
            print("\n" + "=" * 60)
            print("🎤 Voice changer is now running!")
            print("=" * 60)
            print("Access the web interface at:")
            print("  • Local: http://localhost:8000")
            print("  • Network: http://<your-ip>:8000")
            print("\nPress Ctrl+C to stop...")
            print("=" * 60)
            
            # Keep the stream alive
            while True:
                await asyncio.sleep(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Voice changer stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting audio stream: {e}")
        print("Make sure:")
        print("  • Audio devices are properly connected")
        print("  • No other applications are using the audio device")
        print("  • You're running in the SpaceBalls virtual environment")

async def main():
    print("=" * 60)
    print("🎭 Dark Helmet Voice Changer - SpaceBalls Edition")
    print("=" * 60)
    
    # Check virtual environment
    check_virtual_environment()
    
    # Display system information
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.system()} {platform.machine()}")
    
    # Start web server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print(f"🌐 Web interface started at http://0.0.0.0:8000")
    
    try:
        # Find the best audio configuration
        print("\n🔧 Configuring audio system...")
        device_id, sample_rate, channels, blocksize = get_best_audio_config()
        
        # Update global variables with working configuration
        global SAMPLE_RATE, CHANNELS, BLOCK_SIZE
        SAMPLE_RATE = sample_rate
        CHANNELS = channels
        BLOCK_SIZE = blocksize
        
        print(f"\n✅ Using audio configuration:")
        print(f"   Device: {device_id if device_id else 'System Default'}")
        print(f"   Sample rate: {sample_rate}Hz")
        print(f"   Channels: {channels}")
        print(f"   Block size: {blocksize}")
        
        # Update the audio callback to know the current sample rate
        def audio_callback_with_config(indata, outdata, frames, time, status):
            """Audio callback with current configuration"""
            if status:
                print(f"Audio callback status: {status}")
            
            try:
                # Handle different input/output channel configurations
                input_data = indata.copy()
                
                # Convert to mono if needed for processing
                if input_data.ndim == 2 and input_data.shape[1] > 1:
                    mono_input = np.mean(input_data, axis=1, keepdims=True)
                else:
                    mono_input = input_data
                
                # Apply notch filter to reduce feedback
                notch_freq = 1000  # Hz
                Q = 30.0
                try:
                    b, a = signal.iirnotch(notch_freq / (sample_rate / 2), Q)
                    filtered_data = signal.lfilter(b, a, mono_input, axis=0)
                except:
                    filtered_data = mono_input
                
                # Apply voice effects
                try:
                    processed = apply_effects_realtime(filtered_data)
                except:
                    processed = apply_basic_effects(filtered_data)
                
                # Match output channels
                if outdata.ndim == 2:
                    if processed.ndim == 1 or processed.shape[1] == 1:
                        # Duplicate mono to stereo
                        mono_data = processed.flatten()[:frames]
                        outdata[:len(mono_data), 0] = mono_data
                        if outdata.shape[1] > 1:
                            outdata[:len(mono_data), 1] = mono_data
                        # Fill remaining with zeros
                        if len(mono_data) < frames:
                            outdata[len(mono_data):] = 0
                    else:
                        outdata[:] = processed[:frames]
                else:
                    outdata[:] = processed[:frames].flatten()
                    
            except Exception as e:
                print(f"Audio processing error: {e}")
                # Silence output on error
                outdata.fill(0)
        
        # Start audio stream with the working configuration
        with sd.Stream(device=(device_id, device_id) if device_id else None,
                       samplerate=sample_rate,
                       blocksize=blocksize,
                       channels=channels,
                       callback=audio_callback_with_config,
                       dtype="float32"):
            
            print("\n" + "=" * 60)
            print("🎤 Dark Helmet Voice Changer is now running!")
            print("=" * 60)
            print("🌐 Web interface available at:")
            print("  • Local: http://localhost:8000")
            print("  • Network: http://<your-ip>:8000")
            print("\n🎭 Voice Effects:")
            print("  • Pitch Shift: Adjust Dark Helmet's voice depth")
            print("  • Distortion: Add robotic/helmet effect")
            print("  • Reverb: Simulate helmet acoustics")
            print("  • Volume: Control output level")
            print(f"\n⚙️  Audio: {sample_rate}Hz, {channels}ch, {blocksize} samples")
            print("\n🛑 Press Ctrl+C to stop...")
            print("=" * 60)
            
            # Keep the stream alive
            while True:
                await asyncio.sleep(1)
                
    except KeyboardInterrupt:
        print("\n🛑 Voice changer stopped by user")
        print("May the Schwartz be with you! 🎭")
    except Exception as e:
        print(f"\n❌ Error starting audio stream: {e}")
        print("\n🔧 Troubleshooting:")
        print("  • Check if audio devices are connected and not in use")
        print("  • Try closing other audio applications")
        print("  • Verify ALSA/audio drivers are properly installed")
        print("  • Run 'aplay -l' and 'arecord -l' to check available devices")
        print("  • Ensure you're in the SpaceBalls virtual environment")
        print("\n💡 On Raspberry Pi, try:")
        print("  sudo apt update && sudo apt install alsa-utils pulseaudio")

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())