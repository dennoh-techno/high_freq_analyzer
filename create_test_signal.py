
import numpy as np
import scipy.signal as signal
import soundfile as sf

def generate_chirp(filename, duration, samplerate):
    t = np.linspace(0, duration, int(samplerate * duration))
    # Chirp from 20Hz to 95kHz (just below Nyquist 96kHz)
    w = signal.chirp(t, f0=20, t1=duration, f1=95000, method='linear')
    
    # Normalize to -3dB
    w = w * 0.707
    
    # Save as 24-bit PCM
    sf.write(filename, w, samplerate, subtype='PCM_24')
    print(f"Generated {filename} with SR={samplerate}Hz, Duration={duration}s")

if __name__ == "__main__":
    generate_chirp("test_192kHz.wav", 10.0, 192000)
    print("Test file created.")
