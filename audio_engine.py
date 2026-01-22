
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import queue

class AudioEngine(object):
    def __init__(self):
        self.filename = None
        self.sf_file = None
        self.stream = None
        self.current_frame = 0
        self.is_playing = False
        self.is_playing = False
        self.output_device_id = None
        self.input_device_id = None
        self.input_samplerate = 48000
        
        # Buffer for visualization (stores last N samples)
        self.vis_buffer_size = 4096 
        self.vis_data = np.zeros(self.vis_buffer_size) 
        self.lock = threading.Lock()
        
        # Audio block size
        self.block_size = 2048

    def get_output_devices(self):
        """Returns a list of output devices."""
        devices = []
        try:
            print("Querying output devices...")
            sd_devices = sd.query_devices()
            hostapis = sd.query_hostapis()
            
            for idx, d in enumerate(sd_devices):
                if d['max_output_channels'] > 0:
                    api_name = hostapis[d['hostapi']]['name']
                    name = f"{d['name']} ({api_name})"
                    # Mark ASIO devices
                    if 'ASIO' in api_name:
                        name = "[ASIO] " + name
                    devices.append({'id': idx, 'name': name, 'info': d})
            
        except Exception as e:
            print(f"Error querying output devices: {e}")
        return devices

    def get_input_devices(self):
        """Returns a list of input devices."""
        devices = []
        try:
            print("Querying input devices...")
            sd_devices = sd.query_devices()
            hostapis = sd.query_hostapis()
            
            for idx, d in enumerate(sd_devices):
                if d['max_input_channels'] > 0:
                    api_name = hostapis[d['hostapi']]['name']
                    name = f"{d['name']} ({api_name})"
                    if 'ASIO' in api_name:
                        name = "[ASIO] " + name
                    devices.append({'id': idx, 'name': name, 'info': d})
            
        except Exception as e:
            print(f"Error querying input devices: {e}")
        return devices

    def set_output_device(self, device_id):
        print(f"Selecting output device ID: {device_id}")
        self.output_device_id = device_id

    def set_input_device(self, device_id):
        print(f"Selecting input device ID: {device_id}")
        self.input_device_id = device_id

    def load_file(self, filename):
        self.stop()
        self.filename = filename
        try:
            self.sf_file = sf.SoundFile(self.filename)
            self.current_frame = 0
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False

    def play(self):
        if not self.sf_file:
            return
        
        if self.is_playing:
            return

        try:
            samplerate = self.sf_file.samplerate
            channels = self.sf_file.channels
            
            # sounddevice callback
            def callback(outdata, frames, time, status):
                if status:
                    print(status)
                
                data = self.sf_file.read(frames, dtype='float32', always_2d=True)
                
                # Handling end of file
                if len(data) < frames:
                    outdata[:len(data)] = data
                    outdata[len(data):] = 0
                    raise sd.CallbackStop
                else:
                    outdata[:] = data
                
                # Update visualization buffer (using mono mix for simplicity)
                # If stereo, average channels
                mono_data = data.mean(axis=1)
                
                with self.lock:
                    # Roll buffer and add new data
                    # For efficiency in python, maybe just overwrite if buffer size matches data size
                    # But block size (frames) might vary or be small.
                    # Let's keep a fixed size buffer for FFT
                    
                    if len(mono_data) >= self.vis_buffer_size:
                        self.vis_data[:] = mono_data[-self.vis_buffer_size:]
                    else:
                        self.vis_data = np.roll(self.vis_data, -len(mono_data))
                        self.vis_data[-len(mono_data):] = mono_data

            self.stream = sd.OutputStream(
                samplerate=samplerate,
                device=self.output_device_id,
                channels=channels,
                callback=callback,
                blocksize=self.block_size
            )
            self.stream.start()
            self.is_playing = True
            
        except Exception as e:
            print(f"Error starting playback: {e}")
            self.is_playing = False

    def pause(self):
        if self.stream:
            self.stream.stop()
        self.is_playing = False

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        self.stream = None
        self.is_playing = False
        if self.sf_file:
            self.sf_file.seek(0)

    def start_listening(self):
        """Starts monitoring the microphone input."""
        if self.is_playing:
            return

        try:
            # Determine samplerate (try 192kHz, fallback to 48kHz if failed, or device default)
            # ideally getting device default samplerate
            self.input_samplerate = 192000
            if self.input_device_id is not None:
                try:
                    info = sd.query_devices(self.input_device_id)
                    # Try to use high, but respect defaults
                    pass
                except:
                    pass
            
            # sounddevice callback for input
            def callback(indata, frames, time, status):
                if status:
                    print(status)
                
                # indata shape is (frames, channels)
                # Mix to mono
                mono_data = indata.mean(axis=1)
                
                with self.lock:
                    if len(mono_data) >= self.vis_buffer_size:
                        self.vis_data[:] = mono_data[-self.vis_buffer_size:]
                    else:
                        self.vis_data = np.roll(self.vis_data, -len(mono_data))
                        self.vis_data[-len(mono_data):] = mono_data

            self.stream = sd.InputStream(
                samplerate=self.input_samplerate,
                device=self.input_device_id,
                channels=1, # Request mono input
                callback=callback,
                blocksize=self.block_size
            )
            self.stream.start()
            self.is_playing = True
            print(f"Started listening on device {self.input_device_id} at {self.input_samplerate}Hz")
            
        except Exception as e:
            print(f"Error starting input stream: {e}")
            self.is_playing = False

    def get_audio_data(self):
        """Returns the current audio buffer for visualization."""
        with self.lock:
            return self.vis_data.copy()

    def get_samplerate(self):
        if self.sf_file:
            return self.sf_file.samplerate
        if self.input_device_id is not None and self.is_playing:
             return self.input_samplerate
        return 44100
