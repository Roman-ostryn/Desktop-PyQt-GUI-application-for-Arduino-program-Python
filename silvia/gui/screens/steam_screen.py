from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class SteamScreen(QWidget):
    def __init__(self, serial, on_back):
        super().__init__()
        self.serial = serial
        self.on_back = on_back
        self.steam_temp_target = 130

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.temp_label = QLabel("Current: -- °C")
        self.temp_label.setStyleSheet("font-size: 24px;")
        
        self.target_label = QLabel(f"Target: {self.steam_temp_target} °C")
        self.target_label.setStyleSheet("font-size: 20px;")
        
        self.status_label = QLabel("Ready for steaming")
        self.status_label.setStyleSheet("font-size: 18px;")
        
        layout.addWidget(self.temp_label)
        layout.addWidget(self.target_label)
        layout.addWidget(self.status_label)

        self.start_button = QPushButton("Heat to Steam Temp")
        self.stop_button = QPushButton("Stop Steam")
        self.back_button = QPushButton("Back")

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)
        
        self.serial.line_received.connect(self.receive_data)

        self.start_button.clicked.connect(self.start_steam)
        self.stop_button.clicked.connect(self.stop_steam)
        self.back_button.clicked.connect(self.on_back)

    def start_steam(self):
        self.serial.send_command("START_STEAM")
        self.status_label.setText("Heating to steam temperature...")

    def stop_steam(self):
        self.serial.send_command("STOP_STEAM")
        self.status_label.setText("Cooling down...")
        
    def receive_data(self, line: str):
        if line.startswith("STATUS"):
            parts = line.split()
            if len(parts) >= 3:
                try:
                    temp = float(parts[2])
                    self.temp_label.setText(f"Current: {temp:.1f} °C")
                    
                    if temp >= self.steam_temp_target - 2:
                        self.status_label.setText("Ready for steaming!")
                    elif "HEATING" in parts[1]:
                        self.status_label.setText("Heating...")
                except:
                    pass
        elif "READY STEAM" in line:
            self.status_label.setText("Steam temperature reached!")
