from PyQt6.QtWidgets import QPushButton, QLabel, QVBoxLayout, QWidget

class HomeScreen(QWidget):
    def __init__(self, serial):
        super().__init__()
        self.serial = serial

        self.label = QLabel("Coffee Machine Ready")
        self.label.setStyleSheet("font-size: 24px;")
        
        self.temp_gauge = QLabel("Temp: -- °C")
        self.temp_gauge.setStyleSheet("font-size: 20px; color: blue;")

        self.brew_btn = QPushButton("Brew")
        self.brew_btn.setStyleSheet("font-size: 20px; padding: 10px;")
        
        self.steam_button = QPushButton("Steam")
        self.flush_button = QPushButton("Flush")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.temp_gauge)
        layout.addWidget(self.brew_btn)
        layout.addWidget(self.steam_button)
        layout.addWidget(self.flush_button)
        
        self.settings_button = QPushButton("Settings")
        layout.addWidget(self.settings_button)
        
        self.start_button = QPushButton("Start")
        layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop")
        layout.addWidget(self.stop_button)


        # Connect to serial data for temperature display
        self.serial.line_received.connect(self.receive_data)
        
        self.setLayout(layout)
        
    def receive_data(self, line: str):
        if line.startswith("STATUS"):
            parts = line.split()
            if len(parts) >= 3:
                try:
                    temp = float(parts[2])
                    self.temp_gauge.setText(f"Temp: {temp:.1f} °C")
                except:
                    pass
