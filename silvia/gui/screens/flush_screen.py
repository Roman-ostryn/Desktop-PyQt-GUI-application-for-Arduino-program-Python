# from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
# from PyQt6.QtCore import Qt

# class FlushScreen(QWidget):
#     def __init__(self, serial, on_back):
#         super().__init__()
#         self.serial = serial
#         self.on_back = on_back

#         layout = QVBoxLayout()
#         layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

#         self.temp_label = QLabel("Temp: -- °C")
#         self.temp_label.setStyleSheet("font-size: 28px;")
#         layout.addWidget(self.temp_label)

#         self.start_button = QPushButton("Start Flush")
#         self.stop_button = QPushButton("Stop Flush")
#         self.back_button = QPushButton("Back")

#         layout.addWidget(self.start_button)
#         layout.addWidget(self.stop_button)
#         layout.addWidget(self.back_button)

#         self.setLayout(layout)

#         self.start_button.clicked.connect(self.start_flush)
#         self.stop_button.clicked.connect(self.stop_flush)
#         self.back_button.clicked.connect(self.on_back)

#     def start_flush(self):
#         self.serial.send_command("START_FLUSH")

#     def stop_flush(self):
#         self.serial.send_command("STOP_FLUSH")

#     def update_temp(self, temp):
#         self.temp_label.setText(f"Temp: {temp:.1f} °C")


from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QTimer
import time

class FlushScreen(QWidget):
    def __init__(self, serial, on_back):
        super().__init__()
        self.serial = serial
        self.on_back = on_back

        self.temp_label = QLabel("Temperature: -- °C")
        self.timer_label = QLabel("Time: 00:00")

        font = "font-size: 18px;"
        self.temp_label.setStyleSheet(font)
        self.timer_label.setStyleSheet(font)

        self.start_btn = QPushButton("FLUSH")
        self.stop_btn = QPushButton("STOP FLUSH")
        self.back_btn = QPushButton("Back")

        self.start_btn.clicked.connect(self.start_flush)
        self.stop_btn.clicked.connect(self.stop_flush)
        self.back_btn.clicked.connect(self.on_back)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.start_time = None

        self.serial.line_received.connect(self.receive_data)

        layout = QVBoxLayout()
        layout.addWidget(self.temp_label)
        layout.addWidget(self.timer_label)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.back_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def start_flush(self):
        self.serial.send_command("START_FLUSH")
        self.start_time = time.time()
        self.timer.start(1000)

    def stop_flush(self):
        self.serial.send_command("STOP_FLUSH")
        self.timer.stop()

    def update_timer(self):
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.setText(f"Time: {minutes:02}:{seconds:02}")

    def receive_data(self, line: str):
        if "TEMP:" in line:
            try:
                temp = float(line.split("TEMP:")[1].split("°")[0])
                self.temp_label.setText(f"Temperature: {temp:.1f} °C")
            except:
                pass
