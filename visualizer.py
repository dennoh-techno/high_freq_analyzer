
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import QTimer
from scipy.signal import get_window

class SpectrumWidget(pg.PlotWidget):
    def __init__(self, audio_engine, parent=None):
        super().__init__(parent)
        self.audio_engine = audio_engine
        
        # Setup plot style
        self.setBackground('k')
        self.setTitle("Frequency Spectrum")
        self.setLabel('left', 'Amplitude', units='dB')
        self.setLabel('bottom', 'Frequency', units='Hz')
        self.showGrid(x=True, y=True, alpha=0.3)
        
        # Plot curve
        # Use 'stepMode="center"' or just line plot. Line plot is faster usually.
        # fillLevel sets the area under curve. 
        self.plot_data = self.plot(pen=pg.mkPen('c', width=1), brush=pg.mkBrush(0, 255, 255, 50), fillLevel=-140)
        
        # FFT params
        self.window = None
        self.last_buffer_size = 0
        
        # Timer for updating plot
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(30) # ~30-60 FPS

    def update_plot(self):
        if not self.audio_engine.is_playing:
            return

        # Get audio data
        data = self.audio_engine.get_audio_data()
        fs = self.audio_engine.get_samplerate()
        
        if len(data) == 0:
            return
            
        # Apply window function if buffer size changed
        N = len(data)
        if self.last_buffer_size != N:
            self.window = get_window('hann', N)
            self.last_buffer_size = N
        
        # FFT
        # Apply window
        windowed_data = data * self.window
        fft_result = np.fft.rfft(windowed_data)
        
        # Calculate magnitude in dB
        # Add epsilon to avoid log(0)
        magnitude = np.abs(fft_result)
        magnitude = 20 * np.log10(magnitude + 1e-9)
        
        # Frequency axis
        freqs = np.fft.rfftfreq(N, d=1./fs)
        
        # Update plot
        self.plot_data.setData(freqs, magnitude)
        
        # Dynamic range adjustments if needed, but auto-scaling usually works or fixed range
        # Let's fix Y range to generic audio levels
        self.setYRange(-120, 0)
        self.setXRange(0, fs/2)

    def closeEvent(self, event):
        self.timer.stop()
        super().closeEvent(event)
