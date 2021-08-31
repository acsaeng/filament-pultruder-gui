import tkinter as tk
from tkinter.font import Font
from tkinter import messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

# from gpiozero import LED
# import RPi.GPIO

# Initialize Raspberry Pi
# RPi.GPIO.setmode(RPi.GPIO.BCM)

# Set width and height resolutions of the monitor
res_width = 1920
res_height = 1080


class PultrusionInterface(tk.Tk):
	"""A class used to represent the interface for a filament pultruder device

		Attributes:
			Various
		
		Methods:
			initialize_interface(): Initialize the layout and contents of the GUI
			test_motor(): Manually run the motor at a user-specified speed and direction
			run_system(): Begin the operation of the filament pultruder device
			timer(): Operate the timer while running the device
			pause_system(): Pause the current operation on the device
			restart_system(): Restart the system to its initial state
	"""
	def __init__(self,parent):		
		tk.Tk.__init__(self, parent)

		# Define Interface Fonts
		self.header1 = Font(family="Helvetica", size=14, weight="bold")
		self.header2 = Font(family="Helvetica", size=12, weight="bold")
		self.default_text = Font(family="Helvetica", size=12)

		# Generate the properties of each frame
		self.main_pane = tk.PanedWindow(orient=tk.VERTICAL)
		self.main_pane.pack(fill=tk.BOTH, expand=1)

		self.process_plots_frame = tk.LabelFrame(self.main_pane, text="PROCESS PLOTS", font=self.header1, labelanchor=tk.N, width=res_width, height=0.6 * res_height)
		self.process_plots_frame.grid_propagate(0)
		self.main_pane.add(self.process_plots_frame, pady=5)

		self.middle_pane = tk.PanedWindow(self.main_pane, orient=tk.HORIZONTAL)
		self.main_pane.add(self.middle_pane)

		self.test_motor_frame = tk.LabelFrame(self.middle_pane, text="TEST MOTOR", font=self.header1, labelanchor=tk.N, width=res_width / 2, height=0.2 * res_height - 50)
		self.test_motor_frame.grid_propagate(0)
		self.middle_pane.add(self.test_motor_frame, pady=5)

		self.run_system_frame = tk.LabelFrame(self.middle_pane, text="RUN SYSTEM", font=self.header1, labelanchor=tk.N, width=res_width / 2, height=-0.2 * res_height - 50)
		self.run_system_frame.grid_propagate(0)
		self.middle_pane.add(self.run_system_frame, pady=5)

		self.bottom_pane = tk.PanedWindow(self.main_pane, orient=tk.HORIZONTAL)
		self.main_pane.add(self.bottom_pane)

		self.set_parameters_frame = tk.LabelFrame(self.bottom_pane, text="SET PARAMETERS", font=self.header1, labelanchor=tk.N, width=res_width / 2, height=0.2 * res_height - 50)
		self.set_parameters_frame.grid_propagate(0)
		self.bottom_pane.add(self.set_parameters_frame, pady=5)

		self.filament_status_frame = tk.LabelFrame(self.bottom_pane, text="FILAMENT STATUS", font=self.header1, labelanchor=tk.N, width=res_width / 2, height=0.2 * res_height - 50)
		self.filament_status_frame.grid_propagate(0)
		self.bottom_pane.add(self.filament_status_frame, pady=5)
		
		# Organize the frame into a grid layout
		self.process_plots_frame.grid_rowconfigure(0, weight=1)
		self.process_plots_frame.grid_rowconfigure(1, weight=1)
		self.process_plots_frame.grid_columnconfigure(0, weight=1)
		
		self.test_motor_frame.grid_rowconfigure(0, weight=1)
		self.test_motor_frame.grid_rowconfigure(1, weight=1)
		self.test_motor_frame.grid_columnconfigure(0, weight=100)
		self.test_motor_frame.grid_columnconfigure(1, weight=109)

		self.run_system_frame.grid_rowconfigure(0, weight=1)
		self.run_system_frame.grid_rowconfigure(1, weight=1)
		self.run_system_frame.grid_rowconfigure(2, weight=1)
		self.run_system_frame.grid_columnconfigure(0, weight=1)
		self.run_system_frame.grid_columnconfigure(1, weight=1)
		
		self.set_parameters_frame.grid_rowconfigure(0, weight=5)
		self.set_parameters_frame.grid_rowconfigure(1, weight=10)
		self.set_parameters_frame.grid_rowconfigure(2, weight=10)
		self.set_parameters_frame.grid_columnconfigure(0, weight=1)
		self.set_parameters_frame.grid_columnconfigure(1, weight=1)
		
		self.filament_status_frame.grid_rowconfigure(0, weight=1)
		self.filament_status_frame.grid_rowconfigure(1, weight=1)
		self.filament_status_frame.grid_rowconfigure(2, weight=1)
		self.filament_status_frame.grid_rowconfigure(3, weight=1)
		self.filament_status_frame.grid_columnconfigure(0, weight=4)
		self.filament_status_frame.grid_columnconfigure(1, weight=5)
		
		# Initialize the contents of each frame
		self.initialize_interface()
	
	def initialize_interface(self):
		"""Initialize the layout and contents of the GUI
		
            Parameters:
                None
            
            Returns:
                None
		"""
		# Define "Process Plots" frame contents				
		self.line_tension_figure = Figure(figsize=(24, 12), dpi=100, tight_layout=1)
		self.line_tension_plot = self.line_tension_figure.add_subplot(111)
		self.line_tension_plot.set_ylabel("Line Tension (N)")
		self.line_tension_plot.plot()

		self.line_tension_canvas = FigureCanvasTkAgg(self.line_tension_figure, master=self.process_plots_frame)
		self.line_tension_canvas.draw()
		self.line_tension_canvas.get_tk_widget().grid(row=0, column=0, sticky="N")
		
		self.line_speed_figure = Figure(figsize=(24, 12), dpi=100, tight_layout=1)
		self.line_speed_plot = self.line_speed_figure.add_subplot(111)
		self.line_speed_plot.set_xlabel("Time (s)")
		self.line_speed_plot.set_ylabel("Line Speed (mm/min)")
		self.line_speed_plot.plot()

		self.line_speed_canvas = FigureCanvasTkAgg(self.line_speed_figure, master=self.process_plots_frame) 
		self.line_speed_canvas.draw()
		self.line_speed_canvas.get_tk_widget().grid(row=1, column=0, sticky="N")

		# Define "Test Motor" frame contents and initialize properties
		self.manual_motor_speed_label = tk.Label(self.test_motor_frame, text="Manual Motor Speed (mm/min):", font=self.default_text)
		self.manual_motor_speed_label.grid(row=0, column=0, sticky="E", padx=25)
		
		self.manual_motor_speed_entry = tk.Entry(self.test_motor_frame, width=30)
		self.manual_motor_speed_entry.insert(0, "0")
		self.manual_motor_speed_entry.grid(row=0, column=1, sticky="W")

		self.cw_motor_button = tk.Button(self.test_motor_frame, text="Drive CW", command=self.test_motor, width=10)
		self.cw_motor_button.grid(row=1, column=0, sticky="NE", padx=25)
		
		self.ccw_motor_button = tk.Button(self.test_motor_frame, text="Drive CCW", command=self.test_motor, width=10)
		self.ccw_motor_button.grid(row=1, column=1, sticky="NW", padx=25)

		self.motor_speed = 0

		# Define "Run System" frame contents and initialize properties
		self.system_status = tk.Label(self.run_system_frame, text="Status:", font=self.header2)
		self.system_status.grid(row=0, column=0, sticky="SE", padx=10)
		
		self.system_status = tk.Label(self.run_system_frame, text="INACTIVE", font=self.default_text, fg="red")
		self.system_status.grid(row=0, column=1, sticky="SW", padx=10)
		
		self.start_button = tk.Button(self.run_system_frame, text="START", font=self.header2, bg="lightgreen", command=self.run_system, width=25, height=1)
		self.start_button.grid(row=1, column=0, columnspan=2, padx=20)
		
		self.restart_button = tk.Button(self.run_system_frame, text="RESTART", font=self.header2, bg="lightyellow", command=self.restart_system, width=10, height=1)
		self.restart_button.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 5))
		
		# Define "Set Parameters" frame contents and initialize properties
		self.filament_length_label = tk.Label(self.set_parameters_frame, text="Filament Length (m):", font=self.default_text)
		self.filament_length_label.grid(row=0, column=0, sticky="SE", padx=20)

		self.filament_length_entry = tk.Entry(self.set_parameters_frame, width=30)
		self.filament_length_entry.grid(row=0, column=1, sticky="SW", padx=20)
		
		self.line_speed_label = tk.Label(self.set_parameters_frame, text="Line Speed (mm/min):", font=self.default_text)
		self.line_speed_label.grid(row=1, column=0, sticky="E", padx=20)

		self.line_speed_entry = tk.Entry(self.set_parameters_frame, width=30)
		self.line_speed_entry.grid(row=1, column=1, sticky="W", padx=20)

		self.breaking_force_label = tk.Label(self.set_parameters_frame, text="Filament Breaking Force (N):", font=self.default_text)
		self.breaking_force_label.grid(row=2, column=0, sticky="NE", padx=20)

		self.breaking_force_entry = tk.Entry(self.set_parameters_frame, width=30)
		self.breaking_force_entry.grid(row=2, column=1, sticky="NW", padx=20)
		
		# Define "Filament Status" frame contents and initialize properties
		self.duration_label = tk.Label(self.filament_status_frame, text="Duration:", font=self.header2)
		self.duration_label.grid(row=0, column=0, sticky="E", padx=20, pady=(10, 0))
		
		self.duration_value = tk.Label(self.filament_status_frame, text="00:00:00", font=self.default_text)
		self.duration_value.grid(row=0, column=1, sticky="W", padx=20, pady=(10, 0))
		
		self.length_label = tk.Label(self.filament_status_frame, text="Length Produced:", font=self.header2)
		self.length_label.grid(row=1, column=0, sticky="E", padx=20)
		
		self.length_value = tk.Label(self.filament_status_frame, text="0 m", font=self.default_text)
		self.length_value.grid(row=1, column=1, sticky="W", padx=20)
		
		self.completion_label = tk.Label(self.filament_status_frame, text="Percent Completed:", font=self.header2)
		self.completion_label.grid(row=2, column=0, sticky="E", padx=20)
		
		self.completion_value = tk.Label(self.filament_status_frame, text="0 %", font=self.default_text)
		self.completion_value.grid(row=2, column=1, sticky="W", padx=20)
		
		self.pause_flag = False
		self.duration = 0
		self.prev_time = 0

	def test_motor(self):
		"""Manually run the motor at a user-specified speed and direction
		
            Parameters:
                None
            
            Returns:
                None
		"""
		try:
			# Test motor by holding down the CW or CCW button, which drives motor at the inputted speed
			self.motor_speed = float(self.manual_motor_speed_entry.get())
		except ValueError:
			# Catch ValueError if field is empty
			messagebox.showerror("Error", "Error: Manual Motor Speed input must contain a value.")
			raise
		
	def run_system(self):
		"""Begin the operation of the filament pultruder device
		
            Parameters:
                None
            
            Returns:
                None
		"""
		try:
			# Obtain values from filament length, line speed, or breaking force fields
			self.filament_length = float(self.filament_length_entry.get())
			self.line_speed = float(self.line_speed_entry.get())
			self.breaking_force = float(self.breaking_force_entry.get())
		except ValueError:
			# Catch ValueError if fields are empty
			messagebox.showerror("Error", "Error: Filament Length, Line Speed, and Filament Breaking Force inputs must contain values")
			raise
		
		# Change the button and state of the pultruder
		self.start_button.configure(text="STOP", bg="red", command=self.pause_system)
		self.system_status.configure(text="RUNNING", fg="green")
		
		# Start the timer or continue it if it is in a paused state
		if self.pause_flag:
			self.prev_time = self.duration
		
		self.start_time = time.time()
		self.timer()
		
	def timer(self):
		"""Operate the timer while running the device
		
            Parameters:
                None
            
            Returns:
                None
		"""
		# Calculate the duration of the run
		self.duration = self.prev_time + (time.time() - self.start_time)
		
		# Display and continually update timer on the interface using the hh:mm:ss layout
		hours = int(self.duration / 3600)
		minutes = int((self.duration - (hours * 3600)) / 60)
		seconds = int((self.duration - (hours * 3600) - (minutes * 60)))

		self.duration_value.configure(text="{:02d}:{:02d}:{:02d}".format(hours, minutes, seconds))
		self.continue_timer = root.after(1000, self.timer)

	def pause_system(self):
		"""Pause the current operation on the device
		
            Parameters:
                None
            
            Returns:
                None
		"""
		# Prompt use to confirm pause
		self.pause_system_response = messagebox.askyesno("Confirm Pause", "Pause program? Current print will stop.") 	
		
		# If user confirms, pause system and update status
		if self.pause_system_response:
			self.start_button.configure(text = "START", bg = "lightgreen", command = self.run_system)
			self.system_status.configure(text = "PAUSED", fg = "red")
			root.after_cancel(self.continue_timer)
			self.pause_flag = True
	
	def restart_system(self):
		"""Restart the system to its initial state
		
            Parameters:
                None
            
            Returns:
                None
		"""
		# Prompt use to confirm restart
		self.restart_system_response = messagebox.askyesno("Confirm Restart", "Restart program? Current print will be lost.")
		
		# If user confirms, reinitialize the system
		if self.restart_system_response:
			self.initialize_interface()
		
		
if __name__ == "__main__":
	root = PultrusionInterface(None)
	root.title("Filament Pultruder Interface")
	root.mainloop()