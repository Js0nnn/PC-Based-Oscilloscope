# PC-Based Oscilloscope

This repository contains the source code and instructions for a dual-channel PC-based oscilloscope using an Arduino, an ADS1115 ADC, and Python. It visualizes real-time data on two channels (A0 and A1) through a GUI built with `Tkinter` and plots using `Matplotlib`. This Arduino-based circuit can measure both AC and DC voltages ranging from ±30V. The design is suitable for low to medium voltage measurements and can be used for a variety of applications, such as monitoring power supplies, sensing battery voltage, or interfacing with analog circuits.

## Features
- Dual-channel signal visualization.
- Real-time data plotting using Python's Matplotlib.
- Adjustable zoom scales for both X and Y axes.
- Real-time calculations for amplitude, frequency, peak-to-peak, RMS, and more.
- Toggle offset correction for each channel.
- Simple and intuitive graphical interface using Tkinter.

## Components
- **Arduino**: Reads analog signals and sends them to the PC via serial communication.
- **ADS1115 ADC**: Provides precise analog-to-digital conversion.
- **Python**: Processes and visualizes data.

## Requirements

### Hardware:
- Arduino (Uno, Nano, or similar)
- ADS1115 (ADC Module)
- Voltage divider and virtual ground setup (if needed)
- Wires, breadboard, etc.

### Software:
- Python 3.x
- Arduino IDE
- Required Python Libraries:
  ```bash
  pip install pyserial matplotlib numpy
  ```

## Setup and Installation

### 1. **Arduino Setup**:
   - Connect the ADS1115 to the Arduino using I2C.
   - Connect your analog signal inputs to the ADS1115.
   - Upload the Arduino code provided in the `arduino_code.ino` file.

### 2. **Python Setup**:
   - Clone this repository:
     ```bash
     git clone https://github.com/Js0nnn/PC-Based-Oscilloscope.git
     ```
   - Navigate to the directory:
     ```bash
     cd PC-Based-Oscilloscope
     ```
   - Install required Python libraries:
     ```bash
     pip install pyserial matplotlib numpy
     ```

### 3. **Running the Python Script**:
   - Connect your Arduino to the PC via USB.
   - Make sure to adjust the `serial` port in the Python code (`COM3` is the default; change it according to your system).
   - Run the Python script:
     ```bash
     python oscilloscope.py
     ```

## How It Works

### **Arduino Code**:
   The Arduino reads voltage data from the ADS1115 on two channels (A0 and A1), adjusts the values using a voltage divider factor, and sends the data over a serial connection to the Python script.

### **Python GUI**:
   The Python script reads serial data from the Arduino and displays the live waveform for both channels. The GUI allows for:
   - Real-time visualization of both channels.
   - Zoom adjustments for better signal clarity.
   - Real-time calculations for amplitude, frequency, RMS, and peak-to-peak voltage.
   - Offset correction toggles for each channel.

## Usage

### Main Features:
- **Plots**: Two real-time signal plots (one for each channel).
- **Zoom Controls**: X and Y axis zoom sliders.
- **Parameter Labels**: Display of amplitude, frequency, peak-to-peak, RMS, and mean values for each channel.
- **Offset Correction**: Enable/Disable offset correction for better signal viewing.

### Adjusting Serial Port:
Make sure to update the `serial` port in the Python code (`COM3` by default) to match the one your Arduino is connected to.

### Serial Data Format:
The Arduino sends data in the format:
```
A0: <value> A1: <value>
```
Where `<value>` is the adjusted voltage from each channel.

## Limitations
- This circuit can measure a AC signal with a frequency of only upto 100Hz. This is limitted by the external ADC (ADS1115) used and the Arduino UNO's max. sampling rate.
- For now instead of an actual 2.5V voltage reference IC, another buck converter is used to vary the zero offset.
- This circuit does not have any protection circiut in the input to limit overvoltage and surpass voltage spikes.

## Acknowledgments
- [Arduino](https://www.arduino.cc/)
- [Matplotlib](https://matplotlib.org/)
- [ADS1115 Library](https://github.com/RobTillaart/ADS1X15)
  
---

### Enjoy experimenting with this versatile voltage measurement circuit! It's a simple yet powerful design that opens up countless possibilities for your projects. Happy tinkering and have fun exploring the world of voltage sensing!
