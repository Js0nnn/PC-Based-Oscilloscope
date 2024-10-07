import serial
import tkinter as tk
from tkinter import ttk
from tkinter import Scale
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
import numpy as np

# Initialize serial communication
def initialize_serial(port='COM3', baudrate=115200, timeout=0.5):
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None

# GUI setup
def setup_gui(root):
    root.title("Dual-Screen Oscilloscope")
    root.geometry('2000x900')
    root.configure(bg='#1e1e1e')

def create_plot_frame(parent, side, expand=True):
    frame = ttk.Frame(parent, style='TFrame')
    frame.pack(side=side, padx=10, pady=10, fill=tk.BOTH, expand=expand)
    return frame

def create_plot(ax, color, title, ylabel):
    ax.plot([], [], lw=2, color=color)
    ax.set_xlim(0, 200)
    ax.set_ylim(-31, 31)
    ax.set_title(title, color='white', fontsize=16)
    ax.set_xlabel('Time', color='white')
    ax.set_ylabel(ylabel, color='white')

    # Set grid lines
    ax.grid(True, which='both', axis='both', color='gray', linestyle='--', linewidth=0.5)

    # Customize spines and ticks
    ax.spines['top'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(axis='y', colors='white')
    ax.tick_params(axis='x', colors='white', length=0)  # Hide x-axis ticks

    # Hide x-axis labels
    ax.set_xticklabels([])
    ax.set_xticks([])



def initialize_plots():
    fig1, ax1 = plt.subplots(facecolor='#2e2e2e')
    fig2, ax2 = plt.subplots(facecolor='#2e2e2e')

    create_plot(ax1, 'red', 'Channel - 1', 'A0 Value')
    create_plot(ax2, 'blue', 'Channel - 2', 'A1 Value')

    return fig1, ax1, fig2, ax2

def create_data_containers():
    x_data = deque(maxlen=200)
    y_data = deque(maxlen=200)
    y_filtered_data = deque(maxlen=200)
    x_data.extend(range(200))
    y_data.extend([0] * 200)
    y_filtered_data.extend([0] * 200)
    return x_data, y_data, y_filtered_data

def moving_average(data, window_size=1):
    if len(data) < window_size:
        return np.mean(data)
    else:
        return np.mean(list(data)[-window_size:])

# Calculation functions
def calculate_amplitude(data):
    return (max(data) - min(data)) / 2

def calculate_frequency(data, sampling_rate=29):
    data = np.array(data)
    
    # Normalize data
    data -= np.mean(data)
    
    # Identify zero-crossings
    zero_crossings = np.where(np.diff(np.sign(data)))[0]
    
    if len(zero_crossings) < 2:
        return 0
    
    # Calculate periods between zero-crossings
    periods = np.diff(zero_crossings) / sampling_rate
    
    if len(periods) == 0:
        return 0
    
    # Calculate average period
    avg_period = np.mean(periods)
    
    # Ensure avg_period is not zero to avoid division by zero
    if avg_period == 0:
        return 0
    
    # Frequency is the inverse of the average period
    return 1 / avg_period

def calculate_peak_to_peak(data):
    return max(data) - min(data)

def calculate_rms(data):
    return np.sqrt(np.mean(np.square(data)))

def calculate_mean(data):
    return np.mean(data)

def calculate_high_low(data):
    return max(data), min(data)

# Function to update labels
def update_labels(param_labels, data):
    amplitude_label, frequency_label, peak_to_peak_label, rms_label, mean_label, high_label, low_label = param_labels
    amplitude_label.config(text=f"  Amplitude  \n  {calculate_amplitude(data):.2f}")
    frequency_label.config(text=f"Frequency\n{calculate_frequency(data):.2f} Hz")
    peak_to_peak_label.config(text=f"Pk-to-Pk\n{calculate_peak_to_peak(data):.2f}")
    rms_label.config(text=f"RMS\n{calculate_rms(data):.2f}")
    mean_label.config(text=f"Mean\n{calculate_mean(data):.2f}")
    high, low = calculate_high_low(data)
    high_label.config(text=f"High\n{high:.2f}")
    low_label.config(text=f"Low\n{low:.2f}")

# Function to initialize plots
def init_plot(line1, line2, x_data, y_filtered_data_A0, y_filtered_data_A1):
    line1.set_data(x_data, y_filtered_data_A0)
    line2.set_data(x_data, y_filtered_data_A1)
    return line1, line2

# Function to correct offset
def correct_offset(data, reference_value=0):
    offset = np.mean(data) - reference_value
    return [d - offset for d in data]

# Function to update plot data
def update_plot(frame, ser, line1, line2, x_data, y_data_A0, y_filtered_data_A0, y_data_A1, y_filtered_data_A1, ax1, ax2, zoom_scale_x_A0, zoom_scale_y_A0, zoom_scale_x_A1, zoom_scale_y_A1, param_labels_A0, param_labels_A1):
    if ser is None:
        return line1, line2

    while ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        print(data)
        try:
            parts = data.split()
            for i in range(len(parts)):
                if parts[i] == "A0:":
                    sensor_value_A0 = float(parts[i + 1])
                    y_data_A0.append(sensor_value_A0)
                    filtered_value_A0 = moving_average(y_data_A0)
                    y_filtered_data_A0.append(filtered_value_A0)

                elif parts[i] == "A1:":
                    sensor_value_A1 = float(parts[i + 1])
                    y_data_A1.append(sensor_value_A1)
                    filtered_value_A1 = moving_average(y_data_A1)
                    y_filtered_data_A1.append(filtered_value_A1)

                    x_data.append(x_data[-1] + 1)

                    # Correcting offset based on toggle
                    if offset_correction_A0.get():
                        y_filtered_data_A0_corrected = correct_offset(y_filtered_data_A0)
                    else:
                        y_filtered_data_A0_corrected = y_filtered_data_A0

                    if offset_correction_A1.get():
                        y_filtered_data_A1_corrected = correct_offset(y_filtered_data_A1)
                    else:
                        y_filtered_data_A1_corrected = y_filtered_data_A1

                    # Update the axes limits
                    ax1.set_xlim(max(0, x_data[-1] - zoom_scale_x_A0.get()), x_data[-1])
                    ax1.set_ylim(-zoom_scale_y_A0.get(), zoom_scale_y_A0.get())
                    ax2.set_xlim(max(0, x_data[-1] - zoom_scale_x_A1.get()), x_data[-1])
                    ax2.set_ylim(-zoom_scale_y_A1.get(), zoom_scale_y_A1.get())

                    # Update the lines with corrected data
                    line1.set_data(x_data, y_filtered_data_A0_corrected)
                    line2.set_data(x_data, y_filtered_data_A1_corrected)

                    # Update the parameter labels
                    update_labels(param_labels_A0, list(y_filtered_data_A0_corrected))
                    update_labels(param_labels_A1, list(y_filtered_data_A1_corrected))
                    break
        except ValueError:
            print(f"Invalid data received: {data}")
        except Exception as e:
            print(f"Error: {e}")
    return line1, line2

# Function to create and pack parameter labels with centralized styling
def create_parameter_labels(parent):
    # Define a style for the frame
    style = ttk.Style()
    style.configure('TFrame', background='#2e2e2e')  # Set background color for the frame

    # Define a style for labels with white foreground and frame background
    label_style = ttk.Style()
    label_style.configure('TLabel', foreground='white', background='#2e2e2e', font=('Helvetica', 12))

    parent.configure(style='TFrame')  # Apply the style to the frame

    labels = {
        'Amplitude': ttk.Label(parent, text="Amplitude\n0.00", style='TLabel'),
        'Frequency': ttk.Label(parent, text="Frequency\n0.00 Hz", style='TLabel'),
        'Peak-to-Peak': ttk.Label(parent, text="Pk-to-Pk\n0.00", style='TLabel'),
        'RMS': ttk.Label(parent, text="RMS\n0.00", style='TLabel'),
        'Mean': ttk.Label(parent, text="Mean\n0.00", style='TLabel'),
        'High': ttk.Label(parent, text="High\n0.00", style='TLabel'),
        'Low': ttk.Label(parent, text="Low\n0.00", style='TLabel')
    }

    for label in labels.values():
        label.pack(pady=10, anchor='center')

    return labels.values()

# Toggle functions
def toggle_offset_correction_A0():
    if offset_correction_A0.get():
        offset_correction_A0.set(False)
        toggle_button_A0.config(bg='#4b4b4b')  # Dark color when turned off
    else:
        offset_correction_A0.set(True)
        toggle_button_A0.config(bg='#7e7e7e')  # Light color when turned on

def toggle_offset_correction_A1():
    if offset_correction_A1.get():
        offset_correction_A1.set(False)
        toggle_button_A1.config(bg='#4b4b4b')  # Dark color when turned off
    else:
        offset_correction_A1.set(True)
        toggle_button_A1.config(bg='#7e7e7e')  # Light color when turned on

def update_plot(frame, ser, line1, line2, x_data, y_data_A0, y_filtered_data_A0, y_data_A1, y_filtered_data_A1, ax1, ax2, zoom_scale_x_A0, zoom_scale_y_A0, zoom_scale_x_A1, zoom_scale_y_A1, param_labels_A0, param_labels_A1):
    if ser is None:
        return line1, line2

    while ser.in_waiting > 0:
        data = ser.readline().decode('utf-8').strip()
        print(data)
        try:
            parts = data.split()
            for i in range(len(parts)):
                if parts[i] == "A0:":
                    sensor_value_A0 = float(parts[i + 1])
                    y_data_A0.append(sensor_value_A0)
                    filtered_value_A0 = moving_average(y_data_A0)
                    y_filtered_data_A0.append(filtered_value_A0)

                elif parts[i] == "A1:":
                    sensor_value_A1 = float(parts[i + 1])
                    y_data_A1.append(sensor_value_A1)
                    filtered_value_A1 = moving_average(y_data_A1)
                    y_filtered_data_A1.append(filtered_value_A1)

                    x_data.append(x_data[-1] + 1)

                    # Correcting offset based on the toggle state
                    if offset_correction_A0.get():
                        y_filtered_data_A0_corrected = correct_offset(y_filtered_data_A0)
                    else:
                        y_filtered_data_A0_corrected = y_filtered_data_A0

                    if offset_correction_A1.get():
                        y_filtered_data_A1_corrected = correct_offset(y_filtered_data_A1)
                    else:
                        y_filtered_data_A1_corrected = y_filtered_data_A1

                    # Update the axes limits
                    ax1.set_xlim(max(0, x_data[-1] - zoom_scale_x_A0.get()), x_data[-1])
                    ax1.set_ylim(-zoom_scale_y_A0.get(), zoom_scale_y_A0.get())
                    ax2.set_xlim(max(0, x_data[-1] - zoom_scale_x_A1.get()), x_data[-1])
                    ax2.set_ylim(-zoom_scale_y_A1.get(), zoom_scale_y_A1.get())

                    # Update the lines with corrected data
                    line1.set_data(x_data, y_filtered_data_A0_corrected)
                    line2.set_data(x_data, y_filtered_data_A1_corrected)

                    # Update the parameter labels
                    update_labels(param_labels_A0, list(y_filtered_data_A0_corrected))
                    update_labels(param_labels_A1, list(y_filtered_data_A1_corrected))
                    break
        except ValueError:
            print(f"Invalid data received: {data}")
        except Exception as e:
            print(f"Error: {e}")
    return line1, line2

def main():
    global offset_correction_A0, offset_correction_A1, toggle_button_A0, toggle_button_A1

    root = tk.Tk()
    setup_gui(root)

    # Initialize BooleanVars after the root window is created
    offset_correction_A0 = tk.BooleanVar(value=True)
    offset_correction_A1 = tk.BooleanVar(value=True)

    ser = initialize_serial()

    plot_frame1 = create_plot_frame(root, tk.LEFT)
    param_frame_A0 = create_plot_frame(root, tk.LEFT, expand=False)
    plot_frame2 = create_plot_frame(root, tk.LEFT)
    param_frame_A1 = create_plot_frame(root, tk.LEFT, expand=False)

    fig1, ax1, fig2, ax2 = initialize_plots()

    x_data_A0, y_data_A0, y_filtered_data_A0 = create_data_containers()
    x_data_A1, y_data_A1, y_filtered_data_A1 = create_data_containers()

    line1, = ax1.get_lines()
    line2, = ax2.get_lines()

    param_labels_A0 = create_parameter_labels(param_frame_A0)
    param_labels_A1 = create_parameter_labels(param_frame_A1)

    zoom_scale_x_A0 = Scale(plot_frame1, from_=50, to=200, orient=tk.HORIZONTAL, label='X-axis Zoom (A0)', length=600, showvalue=0, tickinterval=10, resolution=1, troughcolor='#4b4b4b', bg='#1e1e1e', fg='white', highlightbackground='#333333', highlightthickness=1)
    zoom_scale_x_A0.set(200)
    zoom_scale_x_A0.pack(padx=10, pady=5, side=tk.BOTTOM)

    zoom_scale_x_A1 = Scale(plot_frame2, from_=50, to=200, orient=tk.HORIZONTAL, label='X-axis Zoom (A1)', length=600, showvalue=0, tickinterval=10, resolution=1, troughcolor='#4b4b4b', bg='#1e1e1e', fg='white', highlightbackground='#333333', highlightthickness=1)
    zoom_scale_x_A1.set(200)
    zoom_scale_x_A1.pack(padx=10, pady=5, side=tk.BOTTOM)

    zoom_scale_y_A0 = Scale(plot_frame1, from_=5, to=100, orient=tk.HORIZONTAL, label='Y-axis Zoom (A0)', length=600, showvalue=0, tickinterval=10, resolution=1, troughcolor='#4b4b4b', bg='#1e1e1e', fg='white', highlightbackground='#333333', highlightthickness=1)
    zoom_scale_y_A0.set(31)
    zoom_scale_y_A0.pack(padx=10, pady=5, side=tk.BOTTOM)

    zoom_scale_y_A1 = Scale(plot_frame2, from_=5, to=100, orient=tk.HORIZONTAL, label='Y-axis Zoom (A1)', length=600, showvalue=0, tickinterval=10, resolution=1, troughcolor='#4b4b4b', bg='#1e1e1e', fg='white', highlightbackground='#333333', highlightthickness=1)
    zoom_scale_y_A1.set(31)
    zoom_scale_y_A1.pack(padx=10, pady=5, side=tk.BOTTOM)

    # Create toggle buttons for offset correction
    toggle_button_A0 = tk.Button(plot_frame1, text="Toggle Offset Correction A0", command=toggle_offset_correction_A0, bg='#7e7e7e', fg='white', highlightbackground='#333333', highlightthickness=1)
    toggle_button_A0.pack(pady=10, side=tk.BOTTOM)

    toggle_button_A1 = tk.Button(plot_frame2, text="Toggle Offset Correction A1", command=toggle_offset_correction_A1, bg='#7e7e7e', fg='white', highlightbackground='#333333', highlightthickness=1)
    toggle_button_A1.pack(pady=10, side=tk.BOTTOM)

    canvas1 = FigureCanvasTkAgg(fig1, master=plot_frame1)
    canvas1.draw()
    canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    canvas2 = FigureCanvasTkAgg(fig2, master=plot_frame2)
    canvas2.draw()
    canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    toolbar1 = NavigationToolbar2Tk(canvas1, plot_frame1)
    toolbar1.update()
    canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    toolbar2 = NavigationToolbar2Tk(canvas2, plot_frame2)
    toolbar2.update()
    canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    ani1 = FuncAnimation(fig1, update_plot, fargs=(ser, line1, line2, x_data_A0, y_data_A0, y_filtered_data_A0, y_data_A1, y_filtered_data_A1, ax1, ax2, zoom_scale_x_A0, zoom_scale_y_A0, zoom_scale_x_A1, zoom_scale_y_A1, param_labels_A0, param_labels_A1), init_func=lambda: init_plot(line1, line2, x_data_A0, y_filtered_data_A0, y_filtered_data_A1), interval=10)
    ani2 = FuncAnimation(fig2, update_plot, fargs=(ser, line1, line2, x_data_A0, y_data_A0, y_filtered_data_A0, y_data_A1, y_filtered_data_A1, ax1, ax2, zoom_scale_x_A0, zoom_scale_y_A0, zoom_scale_x_A1, zoom_scale_y_A1, param_labels_A0, param_labels_A1), init_func=lambda: init_plot(line1, line2, x_data_A0, y_filtered_data_A0, y_filtered_data_A1), interval=10)

    root.protocol("WM_DELETE_WINDOW", lambda: (ser.close() if ser else None, root.destroy()))
    root.mainloop()

if __name__== "__main__":
    main()
