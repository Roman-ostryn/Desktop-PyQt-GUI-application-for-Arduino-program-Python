# from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
# from PyQt6.QtCore import QTimer
# import time
# import pyqtgraph as pg

# class BrewScreen(QWidget):
#     def __init__(self, serial, on_back):
#         super().__init__()
#         self.serial = serial
#         self.on_back = on_back

#         # UI Elements
#         self.temp_label = QLabel("Temperature: -- °C")
#         self.pump_label = QLabel("Pump Power: -- %")
#         self.timer_label = QLabel("Time: 00:00")
#         self.weight_label = QLabel("Weight: -- g")
#         self.pressure_label = QLabel("Pressure: -- bar")

#         font = "font-size: 18px;"
#         for label in [self.temp_label, self.pump_label, self.timer_label, self.weight_label, self.pressure_label]:
#             label.setStyleSheet(font)

#         self.start_btn = QPushButton("Start Brew")
#         self.stop_btn = QPushButton("Stop Brew")
#         self.back_btn = QPushButton("Back")

#         self.start_btn.clicked.connect(self.start_brew)
#         self.stop_btn.clicked.connect(self.stop_brew)
#         self.back_btn.clicked.connect(self.on_back)

#         # Plot
#         self.plot_widget = pg.PlotWidget()
#         self.plot_widget.setYRange(0, 16)
#         self.plot_widget.setLabel('left', 'Sensor Values')
#         self.plot_widget.setLabel('bottom', 'Time', units='s')
#         self.weight_curve = self.plot_widget.plot(pen='g', name="Weight")
#         self.pressure_curve = self.plot_widget.plot(pen='r', name="Pressure")

#         self.start_time = None
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_time)

#         self.data_time = []
#         self.data_weight = []
#         self.data_pressure = []

#         # self.serial.data_received.connect(self.receive_data)

#         # Layout
#         info_layout = QVBoxLayout()
#         for widget in [self.temp_label, self.pump_label, self.timer_label,
#                        self.weight_label, self.pressure_label]:
#             info_layout.addWidget(widget)

#         button_layout = QHBoxLayout()
#         button_layout.addWidget(self.start_btn)
#         button_layout.addWidget(self.stop_btn)
#         button_layout.addWidget(self.back_btn)

#         layout = QVBoxLayout()
#         layout.addLayout(info_layout)
#         layout.addLayout(button_layout)
#         layout.addWidget(self.plot_widget)
#         self.setLayout(layout)

#     def start_brew(self):
#         self.start_time = time.time()
#         self.data_time.clear()
#         self.data_weight.clear()
#         self.data_pressure.clear()
#         self.serial.send_command("START_BREW")
#         self.timer.start(1000)

#     def stop_brew(self):
#         self.serial.send_command("STOP_BREW")
#         self.timer.stop()

#     def update_time(self):
#         if self.start_time:
#             elapsed = int(time.time() - self.start_time)
#             minutes = elapsed // 60
#             seconds = elapsed % 60
#             self.timer_label.setText(f"Time: {minutes:02}:{seconds:02}")

#     def receive_data(self, line):
#         parts = line.split()
#         temp, pwm = 92, 75  # Simulate if not included
#         weight = pressure = None

#         for part in parts:
#             if part.startswith("WEIGHT:"):
#                 try:
#                     weight = float(part.split(":")[1].replace("g", ""))
#                 except:
#                     pass
#             elif part.startswith("PRESSURE:"):
#                 try:
#                     pressure = float(part.split(":")[1].replace("bar", ""))
#                 except:
#                     pass

#         self.temp_label.setText(f"Temperature: {temp} °C")
#         self.pump_label.setText(f"Pump Power: {pwm} %")

#         if weight is not None:
#             self.weight_label.setText(f"Weight: {weight:.1f} g")
#         if pressure is not None:
#             self.pressure_label.setText(f"Pressure: {pressure:.1f} bar")

#         if self.start_time and weight is not None and pressure is not None:
#             t = time.time() - self.start_time
#             self.data_time.append(t)
#             self.data_weight.append(weight)
#             self.data_pressure.append(pressure)
#             self.weight_curve.setData(self.data_time, self.data_weight)
#             self.pressure_curve.setData(self.data_time, self.data_pressure)


from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QTimer
import time
import pyqtgraph as pg

class BrewScreen(QWidget):
    def __init__(self, serial, on_back):
        super().__init__()
        self.serial = serial
        self.on_back = on_back

        # UI Elements
        self.temp_label = QLabel("Temperature: -- °C")
        self.pump_label = QLabel("Pump Power: -- %")
        self.timer_label = QLabel("Time: 00:00")
        self.weight_label = QLabel("Weight: -- g")
        self.pressure_label = QLabel("Pressure: -- bar")

        font = "font-size: 18px;"
        for label in [self.temp_label, self.pump_label, self.timer_label, self.weight_label, self.pressure_label]:
            label.setStyleSheet(font)

        self.start_btn = QPushButton("BREW NOW")
        self.stop_btn = QPushButton("STOP")
        self.back_btn = QPushButton("Back")

        self.start_btn.clicked.connect(self.start_brew)
        self.stop_btn.clicked.connect(self.stop_brew)
        self.back_btn.clicked.connect(self.on_back)

        # Plot setup
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setYRange(0, 16)
        self.plot_widget.setLabel('left', 'Sensor Values')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.weight_curve = self.plot_widget.plot(pen='g', name="Weight")
        self.pressure_curve = self.plot_widget.plot(pen='r', name="Pressure")

        self.start_time = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

        self.sim_timer = QTimer()  # Used if mocking data
        self.sim_timer.timeout.connect(lambda: self.receive_data("WEIGHT:20.5g PRESSURE:8.2bar"))

        self.data_time = []
        self.data_weight = []
        self.data_pressure = []

        # 🔌 Connect to incoming serial data (real or mock)
        # self.serial.data_received.connect(self.receive_data)
        self.serial.line_received.connect(self.receive_data)


        # Layout
        info_layout = QVBoxLayout()
        for widget in [self.temp_label, self.pump_label, self.timer_label,
                       self.weight_label, self.pressure_label]:
            info_layout.addWidget(widget)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.back_btn)

        layout = QVBoxLayout()
        layout.addLayout(info_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.plot_widget)
        self.setLayout(layout)

    def start_brew(self):
        # Step 1: Tare the scales first
        self.serial.send_command("TARE_SCALE")
        
        # Step 2: Start brewing sequence
        self.start_time = time.time()
        self.data_time.clear()
        self.data_weight.clear()
        self.data_pressure.clear()
        
        # Step 3: Turn on valve and start pump
        self.serial.send_command("BEGIN_BREW")
        self.timer.start(1000)
        self.sim_timer.start(1000)  # Simulate data if using mock serial

    def stop_brew(self):
        self.serial.send_command("STOP_BREW")
        self.timer.stop()
        self.sim_timer.stop()
        self.timer_label.setText("Time: 00:00")

    def update_time(self):
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.setText(f"Time: {minutes:02}:{seconds:02}")

    def receive_data(self, line):
        parts = line.split()
        temp, pwm = 92, 75  # Simulated fixed values for now
        weight = pressure = None

        for part in parts:
            if part.startswith("WEIGHT:"):
                try:
                    weight = float(part.split(":")[1].replace("g", ""))
                except:
                    pass
            elif part.startswith("PRESSURE:"):
                try:
                    pressure = float(part.split(":")[1].replace("bar", ""))
                except:
                    pass

        self.temp_label.setText(f"Temperature: {temp} °C")
        self.pump_label.setText(f"Pump Power: {pwm} %")

        if weight is not None:
            self.weight_label.setText(f"Weight: {weight:.1f} g")
        if pressure is not None:
            self.pressure_label.setText(f"Pressure: {pressure:.1f} bar")

        if self.start_time and weight is not None and pressure is not None:
            t = time.time() - self.start_time
            self.data_time.append(t)
            self.data_weight.append(weight)
            self.data_pressure.append(pressure)
            self.weight_curve.setData(self.data_time, self.data_weight)
            self.pressure_curve.setData(self.data_time, self.data_pressure)
