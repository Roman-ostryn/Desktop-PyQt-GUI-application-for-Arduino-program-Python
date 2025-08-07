from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox
from PyQt6.QtCore import Qt

class SettingsScreen(QWidget):
    def __init__(self, on_save, on_back):
        super().__init__()
        self.on_save = on_save
        self.on_back = on_back

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.brew_label = QLabel("Set Brew Temp (°C)")
        self.brew_spin = QSpinBox()
        self.brew_spin.setRange(60, 110)
        self.brew_spin.setValue(93)

        self.steam_label = QLabel("Set Steam Temp (°C)")
        self.steam_spin = QSpinBox()
        self.steam_spin.setRange(110, 150)
        self.steam_spin.setValue(130)

        self.save_button = QPushButton("Save")
        self.back_button = QPushButton("Back")

        layout.addWidget(self.brew_label)
        layout.addWidget(self.brew_spin)
        layout.addWidget(self.steam_label)
        layout.addWidget(self.steam_spin)
        layout.addWidget(self.save_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        self.save_button.clicked.connect(self.save_clicked)
        self.back_button.clicked.connect(self.on_back)

    def save_clicked(self):
        brew = self.brew_spin.value()
        steam = self.steam_spin.value()
        self.on_save(brew, steam)
        
    def set_initial_temps(self, brew, steam):
        self.brew_spin.setValue(brew)
        self.steam_spin.setValue(steam)
