
import sounddevice as sd

print("--- Audio Device Check ---")
try:
    print(f"PortAudio version: {sd.get_portaudio_version()}")
    devices = sd.query_devices()
    print(f"\nTotal devices found: {len(devices)}")
    print(devices)
    
    print("\n--- Output Devices ---")
    hostapis = sd.query_hostapis()
    for i, d in enumerate(devices):
        if d['max_output_channels'] > 0:
            api = hostapis[d['hostapi']]['name']
            print(f"ID {i}: {d['name']} ({api}) - Channels: {d['max_output_channels']}")
            
except Exception as e:
    print(f"Error: {e}")

print("\n--------------------------")
