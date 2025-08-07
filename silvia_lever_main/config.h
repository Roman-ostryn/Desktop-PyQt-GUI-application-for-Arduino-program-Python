/*
 * Configuration file for Silvia Lever Coffee Machine
 * Adjust these values for your specific hardware setup
 */

#ifndef CONFIG_H
#define CONFIG_H

// Hardware Pin Definitions
#define POT_PIN A0              // Potentiometer for pump speed control
#define PUMP_PWM_PIN 9          // PWM output for pump motor
#define HEATER_PWM_PIN 15       // PWM output for heater SSR
#define VALVE_PIN 8             // Digital output for valve relay

// PT100 Temperature Sensor (SPI)
#define PT100_CS 10             // Chip Select
#define PT100_MOSI 11           // Master Out Slave In
#define PT100_MISO 12           // Master In Slave Out
#define PT100_CLK 13            // Clock

// Pressure Sensor (I2C via ADS1115)
#define I2C_SDA 18              // I2C Data
#define I2C_SCL 19              // I2C Clock
#define ADS1115_ADDRESS 0x48    // I2C address of ADS1115

// Scale Sensors (HX711)
#define SCALE_DATA_0 20         // Data pin for scale 0
#define SCALE_DATA_1 22         // Data pin for scale 1
#define SCALE_CLK 21            // Shared clock pin for both scales

// Temperature Sensor Calibration
#define RREF 430.0              // Reference resistor value (430Ω for PT100)
#define RNOMINAL 100.0          // Nominal resistance at 0°C (100Ω for PT100)

// Pressure Sensor Calibration  
#define V_ZERO 0.0              // Zero pressure voltage (V) - will be auto-calibrated
#define V_MAX 4.5               // Maximum pressure voltage (V)
#define P_MIN 0.0               // Minimum pressure (bar)
#define P_MAX 16.0              // Maximum pressure (bar)

// Scale Calibration Factors
#define SCALE_CALIB_0 420.0983  // Calibration factor for scale 0
#define SCALE_CALIB_1 421.365   // Calibration factor for scale 1

// Default Temperature Settings
#define DEFAULT_BREW_TEMP 93.0  // Default brew temperature (°C)
#define DEFAULT_STEAM_TEMP 150.0 // Default steam temperature (°C)

// Temperature Control Parameters
#define TEMP_HYSTERESIS_HIGH 5.0  // Full power above target + this value
#define TEMP_HYSTERESIS_MED 1.0   // Medium power above target + this value
#define TEMP_HYSTERESIS_LOW 0.5   // Low power above target + this value

// PWM Values for Temperature Control
#define HEATER_PWM_FULL 255     // Full power PWM value
#define HEATER_PWM_MED 150      // Medium power PWM value
#define HEATER_PWM_LOW 80       // Low power PWM value

// Timing Constants (milliseconds)
#define TEMP_READ_INTERVAL 500      // Temperature reading interval
#define PRESSURE_READ_INTERVAL 100  // Pressure reading interval
#define SCALE_READ_INTERVAL 200     // Scale reading interval
#define TELEMETRY_INTERVAL 250      // Telemetry transmission interval

// Serial Communication
#define SERIAL_BAUD 115200      // Serial communication baud rate

// Safety Limits
#define MAX_BREW_TEMP 100.0     // Maximum allowed brew temperature
#define MAX_STEAM_TEMP 160.0    // Maximum allowed steam temperature
#define MIN_TEMP 10.0           // Minimum reasonable temperature

#endif // CONFIG_H