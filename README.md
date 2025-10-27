# homogenizer-controller
Embedded controller and Python model for a custom ultrasonic homogenizer. Features real-time LCD interface, thermistor sensing, and simulation of bead-induced shear. Built for biological lab use as part of a senior design project in physics and data science.

# Homogenizer Controller – Senior Design Project

This repository contains the embedded control and modeling code for a custom-built ultrasonic homogenizer, developed independently as part of a senior physics design project at NC State.

The system is designed for biological laboratory use, where it breaks down tissue samples using ultrasonic bead agitation. The Arduino-based controller manages the interface, timing, and thermal monitoring.

## 🔧 Features

- **Rotary Encoder Control** – Adjusts operational timer with a physical knob
- **LCD Display** – Shows real-time countdown and thermistor-based temperature readings
- **Thermistor Sensor** – Monitors internal temperature during operation
- **Pushbutton View Toggle** – Switch between timer and temperature displays
- **Buzzer & LED Alert** – Activates on timer completion
- **Modular Design** – Ready for future expansion (motor frequency, logging, etc.)

## 🧪 Project Context

This code was written and implemented independently as part of a senior design project. The system integrates embedded controls, user interface design, thermal sensing, and real-time display management in a lab-ready application.

## 📁 Files

- `Version1.0.ino` — Arduino code for the embedded control system
- `engine1.0.py` — Python simulation model for bead-induced shear and homogenization efficiency

## 🔜 Future Expansion

- Motor RPM monitoring and closed-loop control
- Power driver integration for ultrasonic motor
- CAD enclosure with thermal modeling
- Data logging and real-time feedback visualization

## 👤 Author

**Axel Fraud**  
Physics + Data Science @ NC State  
[LinkedIn](https://www.linkedin.com/in/axel-fraud) · [dataspec.org](https://dataspec.org)
