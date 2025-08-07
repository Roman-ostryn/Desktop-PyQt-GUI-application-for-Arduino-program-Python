/*
 * Silvia Lever Coffee Machine Controller
 * Integrates all hardware components for touchscreen coffee machine control
 * Hardware: Teensy 4.0, PT100 temp sensor, pressure sensor, scales, pump, heater, valve
 */

#include <Adafruit_MAX31865.h>
#include <ADS1115_WE.h>
#include <Wire.h>
#include "HX711.h"
#include "config.h"

// Hardware objects
Adafruit_MAX31865 thermo = Adafruit_MAX31865(PT100_CS, PT100_MOSI, PT100_MISO, PT100_CLK);
ADS1115_WE adc = ADS1115_WE(ADS1115_ADDRESS);
HX711 scale0, scale1;

// System state
enum SystemState {
  STATE_IDLE,
  STATE_HEATING_BREW,
  STATE_HEATING_STEAM,
  STATE_BREWING,
  STATE_STEAMING,
  STATE_FLUSHING
};

struct SystemData {
  SystemState state = STATE_IDLE;
  float brewTemp = DEFAULT_BREW_TEMP;
  float steamTemp = DEFAULT_STEAM_TEMP;
  float currentTemp = 0.0;
  float pressure = 0.0;
  float weight = 0.0;
  int pumpPower = 0;
  bool valveOpen = false;
  bool heaterOn = false;
  unsigned long brewTimer = 0;
  bool scalesTared = false;
} sys;

// Timing variables
unsigned long lastTempRead = 0;
unsigned long lastPressureRead = 0;
unsigned long lastScaleRead = 0;
unsigned long lastSerialSend = 0;

// Calibrated pressure sensor zero voltage
float calibratedVZero = V_ZERO;



void setup() {
  Serial.begin(SERIAL_BAUD);
  
  // Initialize pins
  pinMode(PUMP_PWM_PIN, OUTPUT);
  pinMode(HEATER_PWM_PIN, OUTPUT);
  pinMode(VALVE_PIN, OUTPUT);
  
  // Initialize to safe state
  analogWrite(PUMP_PWM_PIN, 0);
  analogWrite(HEATER_PWM_PIN, 0);
  digitalWrite(VALVE_PIN, LOW);
  
  // Initialize I2C
  Wire.setSDA(I2C_SDA);
  Wire.setSCL(I2C_SCL);
  Wire.begin();
  
  // Initialize sensors
  thermo.begin(MAX31865_3WIRE);
  
  if (!adc.init()) {
    Serial.println("ERROR:ADS1115_INIT_FAILED");
  } else {
    adc.setVoltageRange_mV(ADS1115_RANGE_4096);
    adc.setCompareChannels(ADS1115_COMP_0_GND);
    adc.setMeasureMode(ADS1115_SINGLE);
  }
  
  // Initialize scales with error checking
  scale0.begin(SCALE_DATA_0, SCALE_CLK);
  scale1.begin(SCALE_DATA_1, SCALE_CLK);
  if (!scale0.is_ready() || !scale1.is_ready()) {
    Serial.println("ERROR:SCALES_NOT_READY");
  }
  scale0.set_scale(SCALE_CALIB_0);
  scale1.set_scale(SCALE_CALIB_1);
  
  // Auto-calibrate pressure sensor zero (like original psens_test)
  if (adc.init()) {
    float sumVoltage = 0;
    for (int i = 0; i < 10; i++) {
      adc.startSingleMeasurement();
      while (adc.isBusy()) { delay(1); }
      sumVoltage += adc.getResult_V();
      delay(10);
    }
    calibratedVZero = sumVoltage / 10;
  }
  
  Serial.println("READY");
}

void loop() {
  processSerialCommands();
  updateSensors();
  updateSystemLogic();
  sendTelemetry();
}

void processSerialCommands() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    
    if (cmd.startsWith("SET_TEMP BREW ")) {
      float temp = cmd.substring(14).toFloat();
      if (temp >= MIN_TEMP && temp <= MAX_BREW_TEMP) {
        sys.brewTemp = temp;
        Serial.println("OK:BREW_TEMP_SET");
      } else {
        Serial.println("ERROR:BREW_TEMP_OUT_OF_RANGE");
      }
    }
    else if (cmd.startsWith("SET_TEMP STEAM ")) {
      float temp = cmd.substring(15).toFloat();
      if (temp >= MIN_TEMP && temp <= MAX_STEAM_TEMP) {
        sys.steamTemp = temp;
        Serial.println("OK:STEAM_TEMP_SET");
      } else {
        Serial.println("ERROR:STEAM_TEMP_OUT_OF_RANGE");
      }
    }
    else if (cmd == "START_BREW") {
      if (sys.state == STATE_IDLE) {
        sys.state = STATE_HEATING_BREW;
        Serial.println("OK:BREW_STARTED");
      } else {
        Serial.println("ERROR:NOT_IDLE");
      }
    }
    else if (cmd == "START_STEAM") {
      if (sys.state == STATE_IDLE) {
        sys.state = STATE_HEATING_STEAM;
        Serial.println("OK:STEAM_STARTED");
      } else {
        Serial.println("ERROR:NOT_IDLE");
      }
    }
    else if (cmd == "START_FLUSH") {
      if (sys.state == STATE_IDLE) {
        sys.state = STATE_FLUSHING;
        setValve(true);
        Serial.println("OK:FLUSH_STARTED");
      } else {
        Serial.println("ERROR:NOT_IDLE");
      }
    }
    else if (cmd == "BEGIN_BREW" || cmd == "BREW_NOW") {
      if (sys.state == STATE_HEATING_BREW) {
        sys.state = STATE_BREWING;
        sys.brewTimer = millis();
        tareScales();
        setValve(true);
        Serial.println("OK:BREWING_STARTED");
      } else {
        Serial.println("ERROR:INVALID_STATE_FOR_BREW_NOW");
      }
    }
    else if (cmd == "STOP") {
      stopCurrentOperation();
      Serial.println("OK:STOPPED");
    }
    else if (cmd == "TARE_SCALES") {
      tareScales();
      Serial.println("OK:SCALES_TARED");
    }
    else if (cmd == "GET_STATUS") {
      sendStatus();
    }
    else if (cmd == "PING") {
      Serial.println("PONG");
    }
    else if (cmd == "ABORT") {
      stopCurrentOperation();
      Serial.println("OK:ABORTED");
    }
    else if (cmd.length() > 0) {
      Serial.println("ERROR:UNKNOWN_COMMAND");
    }
  }
}

void updateSensors() {
  unsigned long now = millis();
  
  // Read temperature with fault detection
  if (now - lastTempRead >= TEMP_READ_INTERVAL) {
    sys.currentTemp = thermo.temperature(RNOMINAL, RREF);
    uint8_t fault = thermo.readFault();
    if (fault) {
      Serial.print("ERROR:PT100_FAULT:"); Serial.println(fault, HEX);
      thermo.clearFault();
    }
    lastTempRead = now;
  }
  
  // Read pressure
  if (now - lastPressureRead >= PRESSURE_READ_INTERVAL) {
    adc.startSingleMeasurement();
    while (adc.isBusy()) { delay(1); }
    float voltage = adc.getResult_V();
    sys.pressure = mapPressure(voltage);
    lastPressureRead = now;
  }
  
  // Read scales
  if (now - lastScaleRead >= SCALE_READ_INTERVAL) {
    if (scale0.is_ready() && scale1.is_ready()) {
      float weight0 = scale0.get_units(1);
      float weight1 = scale1.get_units(1);
      sys.weight = weight0 + weight1;
    }
    lastScaleRead = now;
  }
  
  // Read potentiometer for pump control (like original motor_controller_pot)
  int potValue = analogRead(POT_PIN);
  sys.pumpPower = potValue / 4; // Same as original: value/4
}

void updateSystemLogic() {
  switch (sys.state) {
    case STATE_HEATING_BREW:
      controlHeater(sys.brewTemp);
      break;
      
    case STATE_HEATING_STEAM:
      controlHeater(sys.steamTemp);
      break;
      
    case STATE_BREWING:
      controlHeater(sys.brewTemp);
      controlPump(true);
      break;
      
    case STATE_STEAMING:
      controlHeater(sys.steamTemp);
      break;
      
    case STATE_FLUSHING:
      controlPump(true);
      break;
      
    case STATE_IDLE:
    default:
      controlHeater(0);
      controlPump(false);
      setValve(false);
      break;
  }
}

void controlHeater(float targetTemp) {
  if (targetTemp == 0) {
    analogWrite(HEATER_PWM_PIN, 0);
    sys.heaterOn = false;
    return;
  }
  
  float tempDiff = targetTemp - sys.currentTemp;
  int pwmValue = 0;
  
  if (tempDiff > TEMP_HYSTERESIS_HIGH) {
    pwmValue = HEATER_PWM_FULL;
  } else if (tempDiff > TEMP_HYSTERESIS_MED) {
    pwmValue = HEATER_PWM_MED;
  } else if (tempDiff > TEMP_HYSTERESIS_LOW) {
    pwmValue = HEATER_PWM_LOW;
  }
  
  analogWrite(HEATER_PWM_PIN, pwmValue);
  sys.heaterOn = (pwmValue > 0);
}

void controlPump(bool enable) {
  if (enable && (sys.state == STATE_BREWING || sys.state == STATE_FLUSHING)) {
    analogWrite(PUMP_PWM_PIN, sys.pumpPower);
  } else {
    analogWrite(PUMP_PWM_PIN, 0);
  }
}

void setValve(bool open) {
  digitalWrite(VALVE_PIN, open ? HIGH : LOW);
  sys.valveOpen = open;
}

void tareScales() {
  if (scale0.is_ready() && scale1.is_ready()) {
    scale0.tare();
    scale1.tare();
    sys.scalesTared = true;
  } else {
    Serial.println("ERROR:SCALES_NOT_READY_FOR_TARE");
  }
}

void stopCurrentOperation() {
  sys.state = STATE_IDLE;
  analogWrite(PUMP_PWM_PIN, 0);
  analogWrite(HEATER_PWM_PIN, 0);
  setValve(false);
  sys.brewTimer = 0;
}

float mapPressure(float voltage) {
  if (voltage < calibratedVZero) voltage = calibratedVZero;
  return ((voltage - calibratedVZero) / (V_MAX - calibratedVZero)) * P_MAX;
}

void sendTelemetry() {
  unsigned long now = millis();
  if (now - lastSerialSend >= TELEMETRY_INTERVAL) {
    Serial.print("DATA:");
    Serial.print(sys.state); Serial.print(",");
    Serial.print(sys.currentTemp, 1); Serial.print(",");
    Serial.print(sys.pressure, 2); Serial.print(",");
    Serial.print(sys.weight, 1); Serial.print(",");
    Serial.print(map(sys.pumpPower, 0, 255, 0, 100)); Serial.print(",");
    Serial.print(sys.valveOpen ? 1 : 0); Serial.print(",");
    Serial.print(sys.heaterOn ? 1 : 0); Serial.print(",");
    
    if (sys.state == STATE_BREWING && sys.brewTimer > 0) {
      Serial.print((now - sys.brewTimer) / 1000);
    } else {
      Serial.print(0);
    }
    Serial.println();
    
    lastSerialSend = now;
  }
}

void sendStatus() {
  Serial.print("STATUS:");
  Serial.print("state="); Serial.print(sys.state); Serial.print(",");
  Serial.print("temp="); Serial.print(sys.currentTemp, 1); Serial.print(",");
  Serial.print("brewTemp="); Serial.print(sys.brewTemp, 1); Serial.print(",");
  Serial.print("steamTemp="); Serial.print(sys.steamTemp, 1); Serial.print(",");
  Serial.print("pressure="); Serial.print(sys.pressure, 2); Serial.print(",");
  Serial.print("weight="); Serial.print(sys.weight, 1); Serial.print(",");
  Serial.print("pump="); Serial.print(map(sys.pumpPower, 0, 255, 0, 100)); Serial.print(",");
  Serial.print("valve="); Serial.print(sys.valveOpen ? 1 : 0); Serial.print(",");
  Serial.print("heater="); Serial.print(sys.heaterOn ? 1 : 0);
  Serial.println();
}