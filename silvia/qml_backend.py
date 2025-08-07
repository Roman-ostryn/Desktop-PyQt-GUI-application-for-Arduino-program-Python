from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QTimer
import config
from safety_manager import SafetyManager
from data_logger import DataLogger
from temperature_controller import TemperatureController
import atexit

# Import appropriate serial manager based on configuration
if config.USE_MOCK_SERIAL:
    from serialcom.mock_serial_manager import SerialManager
else:
    from serialcom.real_serial_manager import SerialManager

class CoffeeController(QObject):
    # Signals to QML
    temperatureChanged = pyqtSignal(float)
    pressureChanged = pyqtSignal(float)
    weightChanged = pyqtSignal(float)
    stateChanged = pyqtSignal(str)
    brewTimeChanged = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)
    warningIssued = pyqtSignal(str)
    connectionStatusChanged = pyqtSignal(bool)
    heatingStatusChanged = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Initialize components
        self.logger = DataLogger()
        self.safety = SafetyManager()
        self.temp_controller = TemperatureController()
        
        # Serial communication
        if config.USE_MOCK_SERIAL:
            self.serial = SerialManager()
        else:
            self.serial = SerialManager(port=config.SERIAL_PORT, baud_rate=config.SERIAL_BAUD)
        self.serial.line_received.connect(self._handle_serial_data)
        self.connected = False
        self._current_state = "IDLE"
        
        # Connect safety signals
        self.safety.emergencyStop.connect(self._emergency_stop)
        self.safety.warningIssued.connect(self._handle_warning)
        
        # Connect temperature controller
        self.temp_controller.heaterStateChanged.connect(self._handle_heater_change)
        self.temp_controller.targetReached.connect(self._handle_target_reached)
        
        # Brew timer
        self._brew_start_time = None
        self._timer = QTimer()
        self._timer.timeout.connect(self._update_brew_time)
        
        # Connection watchdog
        self._connection_timer = QTimer()
        self._connection_timer.timeout.connect(self._check_connection)
        self._connection_timer.start(5000)  # Check every 5 seconds
        
        # Register shutdown handler
        atexit.register(self._shutdown)
        
        try:
            self.serial.start()
            self.connected = True
            self.connectionStatusChanged.emit(True)
            self.logger.log_command("System started")
        except Exception as e:
            self.logger.log_error(f"Failed to start serial: {e}")
            self.connected = False
            self.connectionStatusChanged.emit(False)
        
    @pyqtSlot(float, float)
    def setTemperatures(self, brew_temp, steam_temp):
        # Apply safety limits
        brew_temp = max(60, min(110, brew_temp))
        steam_temp = max(110, min(150, steam_temp))
        
        self.temp_controller.set_brew_target(brew_temp)
        self.temp_controller.set_steam_target(steam_temp)
        
        if self.connected:
            self.serial.send_command(f"SET_TEMP BREW {brew_temp}")
            self.serial.send_command(f"SET_TEMP STEAM {steam_temp}")
            self.logger.log_command(f"SET_TEMP BREW {brew_temp} STEAM {steam_temp}")
        else:
            self.logger.log_error("Cannot set temperature - not connected")
        
    @pyqtSlot()
    def startBrew(self):
        if not self.connected:
            self.errorOccurred.emit("Cannot start brew - not connected")
            return
            
        # Check if machine is idle
        if hasattr(self, '_current_state') and self._current_state != "IDLE":
            self.errorOccurred.emit("Cannot start brew - machine not idle")
            return
            
        self.temp_controller.set_mode("BREW")
        self.safety.start_brew_timer()
        
        self.serial.send_command("START_BREW")
        self.logger.log_command("START_BREW")
        
    @pyqtSlot()
    def beginBrew(self):
        """Called when temperature is ready and user presses BREW NOW"""
        if not self.connected:
            self.errorOccurred.emit("Cannot begin brew - not connected")
            return
            
        self.serial.send_command("TARE_SCALES")
        self.serial.send_command("BEGIN_BREW")
        
        import time
        self._brew_start_time = time.time()
        self._timer.start(1000)
        
        self.logger.log_command("BEGIN_BREW")
        
    @pyqtSlot()
    def stopBrew(self):
        if self.connected:
            self.serial.send_command("STOP")
            self.logger.log_command("STOP")
            
        self.temp_controller.set_mode("IDLE")
        self.safety.stop_brew_timer()
        self._timer.stop()
        
        # Log brew session if we have data
        if self._brew_start_time:
            import time
            duration = int(time.time() - self._brew_start_time)
            self.logger.log_brew_session(duration, 0, 0)  # TODO: Add actual weight/pressure
            
        self._brew_start_time = None
        self.brewTimeChanged.emit("00:00")
        
    @pyqtSlot()
    def startSteam(self):
        if not self.connected:
            self.errorOccurred.emit("Cannot start steam - not connected")
            return
            
        self.temp_controller.set_mode("STEAM")
        self.safety.start_steam_timer()
        
        self.serial.send_command("START_STEAM")
        self.logger.log_command("START_STEAM")
        
    @pyqtSlot()
    def stopSteam(self):
        if self.connected:
            self.serial.send_command("STOP")
            self.logger.log_command("STOP")
            
        self.temp_controller.set_mode("IDLE")
        self.safety.stop_steam_timer()
        
    @pyqtSlot()
    def startFlush(self):
        if not self.connected:
            self.errorOccurred.emit("Cannot start flush - not connected")
            return
            
        self.serial.send_command("START_FLUSH")
        self.logger.log_command("START_FLUSH")
        
    @pyqtSlot()
    def stopFlush(self):
        if self.connected:
            self.serial.send_command("STOP")
            self.logger.log_command("STOP")
        
    def _handle_serial_data(self, line):
        self.safety.update_data_timestamp()
        self.logger.log_response(line)
        
        if line.startswith("DATA:"):
            # Parse Arduino DATA format: DATA:state,temp,pressure,weight,pump%,valve,heater,brewTime
            try:
                data_part = line[5:]  # Remove "DATA:"
                parts = data_part.split(',')
                if len(parts) >= 7:
                    state_num = int(parts[0])
                    temp = float(parts[1])
                    pressure = float(parts[2])
                    weight = float(parts[3])
                    pump_percent = int(parts[4])
                    valve = int(parts[5])
                    heater = int(parts[6])
                    brew_time = int(parts[7]) if len(parts) > 7 else 0
                    
                    # Convert state number to string
                    state_names = ["IDLE", "HEATING_BREW", "HEATING_STEAM", "BREWING", "STEAMING", "FLUSHING"]
                    state = state_names[state_num] if state_num < len(state_names) else "UNKNOWN"
                    
                    # Store current state for validation
                    self._current_state = state
                    
                    # Safety check temperature
                    if not self.safety.check_temperature(temp):
                        return
                        
                    # Update temperature controller
                    self.temp_controller.update_temperature(temp)
                    
                    # Log sensor data
                    self.logger.log_sensor_data(temp, pressure, weight, state, pump_percent)
                    
                    # Emit to QML
                    self.stateChanged.emit(state)
                    self.temperatureChanged.emit(temp)
                    self.pressureChanged.emit(pressure)
                    self.weightChanged.emit(weight)
                    
            except Exception as e:
                self.logger.log_error(f"Failed to parse DATA: {line} - {e}")
        elif line.startswith("STATUS"):
            # Handle legacy STATUS format for compatibility
            parts = line.split()
            if len(parts) >= 6:
                try:
                    state = parts[1]
                    temp = float(parts[2])
                    pressure = float(parts[3])
                    weight = float(parts[4])
                    pump_pwm = int(parts[5]) if len(parts) > 5 else 0
                    
                    # Safety check temperature
                    if not self.safety.check_temperature(temp):
                        return
                        
                    # Update temperature controller
                    self.temp_controller.update_temperature(temp)
                    
                    # Log sensor data
                    self.logger.log_sensor_data(temp, pressure, weight, state, pump_pwm)
                    
                    # Emit to QML
                    self.stateChanged.emit(state)
                    self.temperatureChanged.emit(temp)
                    self.pressureChanged.emit(pressure)
                    self.weightChanged.emit(weight)
                    
                except Exception as e:
                    self.logger.log_error(f"Failed to parse status: {line} - {e}")
        elif line.startswith("ERROR"):
            self.logger.log_error(line)
            self.errorOccurred.emit(line)
        elif line.startswith("READY") or line.startswith("PONG"):
            self.logger.log_command(f"Received: {line}")
                    
    def _update_brew_time(self):
        if self._brew_start_time:
            import time
            elapsed = int(time.time() - self._brew_start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.brewTimeChanged.emit(f"{minutes:02}:{seconds:02}")
            
    def _emergency_stop(self, reason):
        """Handle emergency stop from safety manager"""
        self.logger.log_safety_event(f"EMERGENCY STOP: {reason}")
        self.errorOccurred.emit(f"EMERGENCY STOP: {reason}")
        
        # Stop all operations
        if self.connected:
            self.serial.send_command("ABORT")
            
        self.temp_controller.set_mode("IDLE")
        self.safety.stop_brew_timer()
        self.safety.stop_steam_timer()
        self._timer.stop()
        
    def _handle_warning(self, warning):
        self.logger.log_warning(warning)
        self.warningIssued.emit(warning)
        
    def _handle_heater_change(self, heating):
        self.heatingStatusChanged.emit(heating)
        # Arduino controls heater internally based on temperature
            
    def _handle_target_reached(self, mode):
        self.logger.log_command(f"Target temperature reached for {mode}")
        
    def _check_connection(self):
        if self.connected and self.serial:
            try:
                self.serial.send_command("PING")
                self.connectionStatusChanged.emit(True)
                # Could add timeout check here if no PONG received
            except Exception as e:
                self.connected = False
                self.connectionStatusChanged.emit(False)
                self.logger.log_error(f"Connection lost: {e}")
                self._attempt_reconnection()
                
    def _attempt_reconnection(self):
        """Try to reconnect after connection loss"""
        try:
            self.logger.log_command("Attempting reconnection...")
            if self.serial:
                self.serial.stop()
            if config.USE_MOCK_SERIAL:
                self.serial = SerialManager()
            else:
                self.serial = SerialManager(port=config.SERIAL_PORT, baud_rate=config.SERIAL_BAUD)
            self.serial.line_received.connect(self._handle_serial_data)
            if self.serial.start():
                self.connected = True
                self.connectionStatusChanged.emit(True)
                self.logger.log_command("Reconnection successful")
            else:
                self.logger.log_error("Reconnection failed")
        except Exception as e:
            self.logger.log_error(f"Reconnection error: {e}")
                
    def _shutdown(self):
        """Clean shutdown procedure"""
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.log_command("Initiating shutdown")
            
            # Stop all operations
            if hasattr(self, 'connected') and self.connected and hasattr(self, 'serial') and self.serial:
                self.serial.send_command("ABORT")
                self.serial.stop()
                
            if hasattr(self, 'temp_controller') and self.temp_controller:
                self.temp_controller.set_mode("IDLE")
            if hasattr(self, '_timer') and self._timer:
                self._timer.stop()
            if hasattr(self, '_connection_timer') and self._connection_timer:
                self._connection_timer.stop()
            
            if hasattr(self, 'logger') and self.logger:
                self.logger.shutdown()
        except RuntimeError:
            # Qt objects already deleted, ignore
            pass
        
    @pyqtSlot()
    def emergencyStop(self):
        """Manual emergency stop from UI"""
        self._emergency_stop("Manual emergency stop")