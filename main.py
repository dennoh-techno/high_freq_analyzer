
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, QComboBox, QMessageBox)
from PyQt6.QtCore import Qt
import audio_engine
import visualizer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("High Frequency Spectrum Analyzer")
        self.resize(1000, 700)

        self.audio = audio_engine.AudioEngine()

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main Layout
        layout = QVBoxLayout(central_widget)

        # Mode Selection Area
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["File Player", "Live Input"])
        self.mode_combo.currentIndexChanged.connect(self.change_mode)
        mode_layout.addWidget(mode_label)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        layout.addLayout(mode_layout)

        # Device Selection Area
        dev_layout = QHBoxLayout()
        
        # Output Device
        out_label = QLabel("Output:")
        self.output_combo = QComboBox()
        self.output_combo.currentIndexChanged.connect(self.change_output_device)
        
        # Input Device
        in_label = QLabel("Input:")
        self.input_combo = QComboBox()
        self.input_combo.currentIndexChanged.connect(self.change_input_device)
        
        dev_layout.addWidget(out_label)
        dev_layout.addWidget(self.output_combo)
        dev_layout.addWidget(in_label)
        dev_layout.addWidget(self.input_combo)
        dev_layout.addStretch()
        layout.addLayout(dev_layout)

        self.refresh_devices()

        # Visualization Area
        self.vis_widget = visualizer.SpectrumWidget(self.audio)
        layout.addWidget(self.vis_widget, stretch=1)

        # Controls Area
        controls_layout = QHBoxLayout()
        
        self.btn_load = QPushButton("Load File")
        self.btn_load.clicked.connect(self.load_file)
        
        self.btn_play = QPushButton("Play")
        self.btn_play.clicked.connect(self.play_audio)
        
        self.btn_pause = QPushButton("Pause")
        self.btn_pause.clicked.connect(self.pause_audio)
        
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.clicked.connect(self.stop_audio)
        
        self.lbl_status = QLabel("No file loaded")

        controls_layout.addWidget(self.btn_load)
        controls_layout.addWidget(self.btn_play)
        controls_layout.addWidget(self.btn_pause)
        controls_layout.addWidget(self.btn_stop)
        controls_layout.addWidget(self.lbl_status)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)

        # Style
        self.apply_styles()

    def refresh_devices(self):
        # Output Devices
        out_devices = self.audio.get_output_devices()
        self.output_combo.blockSignals(True)
        self.output_combo.clear()
        for dev in out_devices:
            self.output_combo.addItem(dev['name'], userData=dev['id'])
        self.output_combo.blockSignals(False)
        if hasattr(self.audio, 'output_device_id') and self.audio.output_device_id is not None:
             pass # Logic to select current, but for now defaults to 0
        elif out_devices:
            self.change_output_device(0)

        # Input Devices
        in_devices = self.audio.get_input_devices()
        self.input_combo.blockSignals(True)
        self.input_combo.clear()
        for dev in in_devices:
            self.input_combo.addItem(dev['name'], userData=dev['id'])
        self.input_combo.blockSignals(False)
        if in_devices:
             self.change_input_device(0)
        
    def change_output_device(self, index):
        if index < 0: return
        device_id = self.output_combo.itemData(index)
        self.audio.set_output_device(device_id)

    def change_input_device(self, index):
        if index < 0: return
        device_id = self.input_combo.itemData(index)
        self.audio.set_input_device(device_id)

    def change_mode(self, index):
        self.audio.stop()
        mode = self.mode_combo.currentText()
        if mode == "File Player":
            self.btn_load.setEnabled(True)
            self.lbl_status.setText("Mode: File Player")
            self.btn_play.setText("Play")
        else:
            self.btn_load.setEnabled(False)
            self.lbl_status.setText("Mode: Live Input")
            self.btn_play.setText("Start Monitor")

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio File", "", "Audio Files (*.wav *.flac *.aiff *.mp3);;All Files (*)")
        if file_path:
            if self.audio.load_file(file_path):
                self.lbl_status.setText(f"Loaded: {file_path.split('/')[-1]} ({self.audio.get_samplerate()} Hz)")
                self.vis_widget.setXRange(0, self.audio.get_samplerate()/2)
            else:
                QMessageBox.critical(self, "Error", "Failed to load file.")

    def play_audio(self):
        mode = self.mode_combo.currentText()
        if mode == "File Player":
            self.audio.play()
        else:
            self.audio.start_listening()

    def pause_audio(self):
        self.audio.pause()

    def stop_audio(self):
        self.audio.stop()

    def apply_styles(self):
        # Simple dark theme
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; color: #ffffff; }
            QLabel { color: #ffffff; font-size: 14px; }
            QPushButton { 
                background-color: #3d3d3d; 
                color: #ffffff; 
                border: 1px solid #555; 
                padding: 5px 15px; 
                font-size: 14px;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #505050; }
            QPushButton:pressed { background-color: #2a2a2a; }
            QComboBox { 
                background-color: #3d3d3d; 
                color: #ffffff; 
                border: 1px solid #555; 
                padding: 5px;
            }
            QComboBox QAbstractItemView { background-color: #3d3d3d; color: #ffffff; }
        """)

    def closeEvent(self, event):
        self.audio.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
