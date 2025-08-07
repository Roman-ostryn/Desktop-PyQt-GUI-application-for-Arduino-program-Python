# Silvia Coffee Machine Installation Guide

## Prerequisites

### Hardware Requirements
- Teensy 4.0 microcontroller
- PT100 temperature sensor with MAX31865 amplifier
- Pressure sensor (Honeywell MIP series) with ADS1115 ADC
- HX711 load cell amplifiers with force sensors
- SSR for heater control
- Pump with PWM control
- Solenoid valve
- Hardware potentiometer for pump speed control

### Software Requirements
- Python 3.8 or higher
- PyQt6
- pyserial (for hardware communication)

## Installation Steps

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Upload Arduino Code
1. Install Arduino IDE with Teensy support
2. Install required libraries:
   - Adafruit MAX31865 library
   - ADS1115_WE library
   - HX711 library
3. Open `silvia_lever_main/silvia_lever_main.ino`
4. Adjust `config.h` for your hardware setup
5. Upload to Teensy 4.0

### 3. Configure Hardware Connection
Edit `config.py`:
- Set `USE_MOCK_SERIAL = False` for real hardware
- Set `SERIAL_PORT` to your Teensy port (or leave None for auto-detection)

## Running the Application

### Testing Mode (Mock Hardware)
```bash
python run_silvia.py --mock
```

### Real Hardware Mode
```bash
# Auto-detect Teensy port
python run_silvia.py

# Specify port manually
python run_silvia.py --port COM3  # Windows
python run_silvia.py --port /dev/ttyUSB0  # Linux
```

### Fullscreen Mode (for touchscreen)
```bash
python run_silvia.py --fullscreen
```

## Hardware Calibration

### Scale Calibration
1. Place known weights on each scale
2. Adjust `SCALE_CALIB_0` and `SCALE_CALIB_1` in `config.h`
3. Re-upload Arduino code

### Pressure Sensor Calibration
- The pressure sensor auto-calibrates zero pressure on startup
- Adjust `P_MAX` in `config.h` if using different pressure range

### Temperature Sensor
- PT100 sensors are pre-calibrated
- Verify `RREF` matches your reference resistor value

## Troubleshooting

### Serial Connection Issues
1. Check Teensy is properly connected
2. Verify correct COM port
3. Ensure no other applications are using the port
4. Try different USB cable

### Sensor Issues
1. Check all wiring connections
2. Verify I2C addresses (ADS1115 default: 0x48)
3. Test each sensor individually with provided test code

### GUI Issues
1. Ensure PyQt6 is properly installed
2. Check QML file paths are correct
3. Verify all SVG icons are present

## Safety Notes

⚠️ **IMPORTANT SAFETY WARNINGS:**
- Never exceed maximum temperature limits
- Always test emergency stop functionality
- Verify all safety interlocks before operation
- Use appropriate electrical safety measures for mains voltage components
- Test all functions thoroughly before first use

## File Structure
```
silvia_lever_main/          # Arduino code
├── silvia_lever_main.ino   # Main Arduino sketch
├── config.h                # Hardware configuration
└── README.md

serialcom/                  # Serial communication
├── mock_serial_manager.py  # Mock hardware for testing
└── real_serial_manager.py  # Real hardware communication

gui/                        # GUI components (legacy)
controls/                   # QML controls
svgs/                       # UI icons
logs/                       # Application logs

main.py                     # Original main entry point
run_silvia.py              # New startup script with options
config.py                  # Application configuration
qml_backend.py             # PyQt6 backend logic
main.qml                   # Main QML interface
requirements.txt           # Python dependencies
```