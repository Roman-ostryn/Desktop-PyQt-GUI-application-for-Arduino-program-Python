from PyQt6.QtCore import QObject, pyqtSignal, QTimer
import random
import time

class SerialManager(QObject):
    line_received = pyqtSignal(str)
    
    # Mirror Arduino state enum
    STATE_IDLE = 0
    STATE_HEATING_BREW = 1
    STATE_HEATING_STEAM = 2
    STATE_BREWING = 3
    STATE_STEAMING = 4
    STATE_FLUSHING = 5
    
    def __init__(self):
        super().__init__()
        self.connected = False
        
        # Mirror Arduino SystemData struct
        self.state = self.STATE_IDLE
        self.brewTemp = 93.0
        self.steamTemp = 130.0
        self.currentTemp = 25.0
        self.pressure = 0.0
        self.weight = 0.0
        self.pumpPower = 0
        self.valveOpen = False
        self.heaterOn = False
        self.brewTimer = 0
        self.scalesTared = False
        
        # Timers
        self.telemetry_timer = QTimer()
        self.telemetry_timer.timeout.connect(self._send_telemetry)
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_system)
        
    def start(self):
        self.connected = True
        self.telemetry_timer.start(250)  # Match Arduino TELEMETRY_INTERVAL
        self.update_timer.start(100)     # System update loop
        self.line_received.emit("READY")
        
    def stop(self):
        self.connected = False
        self.telemetry_timer.stop()
        self.update_timer.stop()
        
    def send_command(self, command):
        if not self.connected:
            return
            
        cmd = command.strip()
        
        # Mirror Arduino command processing exactly
        if cmd.startswith("SET_TEMP BREW "):
            temp = float(cmd[14:])
            if 60 <= temp <= 110:  # MIN_TEMP to MAX_BREW_TEMP
                self.brewTemp = temp
                self.line_received.emit("OK:BREW_TEMP_SET")
            else:
                self.line_received.emit("ERROR:BREW_TEMP_OUT_OF_RANGE")
                
        elif cmd.startswith("SET_TEMP STEAM "):
            temp = float(cmd[15:])
            if 60 <= temp <= 150:  # MIN_TEMP to MAX_STEAM_TEMP
                self.steamTemp = temp
                self.line_received.emit("OK:STEAM_TEMP_SET")
            else:
                self.line_received.emit("ERROR:STEAM_TEMP_OUT_OF_RANGE")
                
        elif cmd == "START_BREW":
            if self.state == self.STATE_IDLE:
                self.state = self.STATE_HEATING_BREW
                self.line_received.emit("OK:BREW_STARTED")
            else:
                self.line_received.emit("ERROR:NOT_IDLE")
                
        elif cmd == "START_STEAM":
            if self.state == self.STATE_IDLE:
                self.state = self.STATE_HEATING_STEAM
                self.line_received.emit("OK:STEAM_STARTED")
            else:
                self.line_received.emit("ERROR:NOT_IDLE")
                
        elif cmd == "START_FLUSH":
            if self.state == self.STATE_IDLE:
                self.state = self.STATE_FLUSHING
                self.valveOpen = True
                self.line_received.emit("OK:FLUSH_STARTED")
            else:
                self.line_received.emit("ERROR:NOT_IDLE")
                
        elif cmd in ["BEGIN_BREW", "BREW_NOW"]:
            if self.state == self.STATE_HEATING_BREW:
                self.state = self.STATE_BREWING
                self.brewTimer = int(time.time() * 1000)  # millis()
                self.scalesTared = True
                self.valveOpen = True
                self.line_received.emit("OK:BREWING_STARTED")
            else:
                self.line_received.emit("ERROR:INVALID_STATE_FOR_BREW_NOW")
                
        elif cmd == "STOP":
            self._stop_current_operation()
            self.line_received.emit("OK:STOPPED")
            
        elif cmd == "TARE_SCALES":
            self.scalesTared = True
            self.line_received.emit("OK:SCALES_TARED")
            
        elif cmd == "GET_STATUS":
            self._send_status()
            
        elif cmd == "PING":
            self.line_received.emit("PONG")
            
        elif cmd == "ABORT":
            self._stop_current_operation()
            self.line_received.emit("OK:ABORTED")
            
        elif len(cmd) > 0:
            self.line_received.emit("ERROR:UNKNOWN_COMMAND")
            
    def _update_system(self):
        # Mirror Arduino updateSystemLogic()
        if self.state == self.STATE_HEATING_BREW:
            self._control_heater(self.brewTemp)
        elif self.state == self.STATE_HEATING_STEAM:
            self._control_heater(self.steamTemp)
        elif self.state == self.STATE_BREWING:
            self._control_heater(self.brewTemp)
            self._control_pump(True)
        elif self.state == self.STATE_STEAMING:
            self._control_heater(self.steamTemp)
        elif self.state == self.STATE_FLUSHING:
            self._control_pump(True)
        else:  # STATE_IDLE
            self._control_heater(0)
            self._control_pump(False)
            self.valveOpen = False
            
        # Update sensors
        self._update_sensors()
        
    def _control_heater(self, targetTemp):
        if targetTemp == 0:
            self.heaterOn = False
            return
            
        tempDiff = targetTemp - self.currentTemp
        if tempDiff > 5.0:  # TEMP_HYSTERESIS_HIGH
            self.heaterOn = True
            # Simulate heating
            self.currentTemp += random.uniform(0.5, 2.0)
        elif tempDiff > 1.0:  # TEMP_HYSTERESIS_MED
            self.heaterOn = True
            self.currentTemp += random.uniform(0.2, 1.0)
        elif tempDiff > 0.5:  # TEMP_HYSTERESIS_LOW
            self.heaterOn = True
            self.currentTemp += random.uniform(0.1, 0.5)
        else:
            self.heaterOn = False
            
        # Natural cooling
        if not self.heaterOn and self.currentTemp > 25:
            self.currentTemp -= random.uniform(0.1, 0.3)
            
        self.currentTemp = max(20, min(160, self.currentTemp))
        
    def _control_pump(self, enable):
        if enable and (self.state == self.STATE_BREWING or self.state == self.STATE_FLUSHING):
            # Simulate potentiometer reading
            self.pumpPower = random.randint(50, 255)
        else:
            self.pumpPower = 0
            
    def _update_sensors(self):
        # Simulate pressure sensor
        if self.state == self.STATE_BREWING and self.pumpPower > 0:
            self.pressure = random.uniform(6, 12)
        else:
            self.pressure = random.uniform(0, 1)
            
        # Simulate weight sensor
        if self.state == self.STATE_BREWING:
            # Simulate coffee extraction
            elapsed = (int(time.time() * 1000) - self.brewTimer) / 1000.0 if self.brewTimer > 0 else 0
            self.weight = min(elapsed * 0.8 + random.uniform(-2, 2), 50)
        else:
            self.weight = random.uniform(-1, 1)
            
    def _stop_current_operation(self):
        self.state = self.STATE_IDLE
        self.pumpPower = 0
        self.heaterOn = False
        self.valveOpen = False
        self.brewTimer = 0
        
    def _send_telemetry(self):
        # Mirror Arduino sendTelemetry() format
        brew_time_sec = 0
        if self.state == self.STATE_BREWING and self.brewTimer > 0:
            brew_time_sec = (int(time.time() * 1000) - self.brewTimer) // 1000
            
        pump_percent = int((self.pumpPower / 255.0) * 100)
        
        data_msg = f"DATA:{self.state},{self.currentTemp:.1f},{self.pressure:.2f},{self.weight:.1f},{pump_percent},{1 if self.valveOpen else 0},{1 if self.heaterOn else 0},{brew_time_sec}"
        self.line_received.emit(data_msg)
        
    def _send_status(self):
        # Mirror Arduino sendStatus() format
        pump_percent = int((self.pumpPower / 255.0) * 100)
        status_msg = f"STATUS:state={self.state},temp={self.currentTemp:.1f},brewTemp={self.brewTemp:.1f},steamTemp={self.steamTemp:.1f},pressure={self.pressure:.2f},weight={self.weight:.1f},pump={pump_percent},valve={1 if self.valveOpen else 0},heater={1 if self.heaterOn else 0}"
        self.line_received.emit(status_msg)