"""
FRIDAY HUD Dashboard - Iron Man JARVIS-inspired Interface
Dark mode with cyan glowing elements, live telemetry, and animated displays.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import datetime
import math
import psutil
import random

# Color Scheme - Iron Man HUD Style
BG = "#050510"
CYAN = "#00d4ff"
CYAN_DIM = "#004455"
GREEN = "#00ff88"
RED = "#ff3333"
ORANGE = "#ff8800"
WHITE = "#ffffff"
DIM = "#223344"
PANEL = "#0a0f1a"


class FridayDashboard:
    """Iron Man FRIDAY HUD Dashboard with live telemetry"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("F.R.I.D.A.Y // MOTU INDUSTRIES")
        self.root.geometry("380x700+1090+50")
        self.root.configure(bg=BG)
        
        # Set window icon if available
        try:
            import os
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "friday_icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            pass  # Icon file not found, continue without it
        
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        self.root.resizable(False, False)
        
        # State variables
        self.status_var = tk.StringVar(value="INITIALIZING")
        self.heard_var = tk.StringVar(value="AWAITING INPUT...")
        self.response_var = tk.StringVar(value="SYSTEM READY")
        self.time_var = tk.StringVar()
        self.cpu_var = tk.StringVar(value="CPU: ---%")
        self.mem_var = tk.StringVar(value="MEM: ---%")
        self.battery_var = tk.StringVar(value="PWR: ---%")
        
        # Animation variables
        self.log_entries = []
        self.pulse_radius = 20
        self.pulse_growing = True
        self.scan_angle = 0
        self.status_color = CYAN
        self.pulse_speed = 2
        
        # UI components
        self.status_label = None
        self.heard_label = None
        self.response_label = None
        self.radar_canvas = None
        self.log_text = None
        self.pulse_canvas = None
        self.cpu_bar = None
        self.mem_bar = None
        self.battery_bar = None
        
        self.build_ui()
        self.start_animations()
    
    def build_ui(self):
        """Build the complete HUD interface"""
        
        # ===== HEADER SECTION =====
        header_canvas = tk.Canvas(self.root, width=380, height=60, bg=BG, highlightthickness=0)
        header_canvas.pack(fill=tk.X)
        
        # Draw hexagon pattern lines
        for i in range(5):
            x = 50 + i * 60
            header_canvas.create_line(x, 10, x + 30, 50, fill=CYAN_DIM, width=1)
        
        # Title
        header_canvas.create_text(
            190, 20,
            text="⬡ F.R.I.D.A.Y",
            font=("Courier New", 18, "bold"),
            fill=CYAN
        )
        
        # Subtitle
        header_canvas.create_text(
            190, 42,
            text="MOTU INDUSTRIES // CORE_SYSTEM_V4.2",
            font=("Courier New", 7),
            fill=DIM
        )
        
        # Separator line
        separator = tk.Frame(self.root, bg=CYAN, height=1)
        separator.pack(fill=tk.X)
        
        # ===== STATUS PANEL =====
        status_frame = tk.Frame(self.root, bg=PANEL, height=100)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Radar canvas
        self.radar_canvas = tk.Canvas(status_frame, width=360, height=70, bg=PANEL, highlightthickness=0)
        self.radar_canvas.pack()
        
        # Status label
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Courier New", 20, "bold"),
            fg=CYAN,
            bg=PANEL
        )
        self.status_label.pack(pady=5)
        
        # ===== METRICS PANEL =====
        metrics_frame = tk.Frame(self.root, bg=PANEL)
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # CPU
        cpu_label = tk.Label(metrics_frame, text="CPU_LOAD", font=("Courier New", 7), fg=CYAN_DIM, bg=PANEL)
        cpu_label.pack(anchor="w")
        self.cpu_bar = ttk.Progressbar(metrics_frame, length=360, mode='determinate', 
                                        style='Cyan.Horizontal.TProgressbar')
        self.cpu_bar.pack(fill=tk.X, pady=(0, 3))
        
        # Memory
        mem_label = tk.Label(metrics_frame, text="MEM_ALLOC", font=("Courier New", 7), fg=GREEN, bg=PANEL)
        mem_label.pack(anchor="w")
        self.mem_bar = ttk.Progressbar(metrics_frame, length=360, mode='determinate')
        self.mem_bar.pack(fill=tk.X, pady=(0, 3))
        
        # Battery
        battery_label = tk.Label(metrics_frame, text="PWR_CORE", font=("Courier New", 7), fg=ORANGE, bg=PANEL)
        battery_label.pack(anchor="w")
        self.battery_bar = ttk.Progressbar(metrics_frame, length=360, mode='determinate')
        self.battery_bar.pack(fill=tk.X)
        
        # Configure progress bar colors
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Cyan.Horizontal.TProgressbar', background=CYAN)
        style.configure('TProgressbar', background=GREEN, troughcolor=DIM)
        
        # ===== INPUT/OUTPUT SECTION =====
        io_frame = tk.Frame(self.root, bg=PANEL, relief=tk.SUNKEN, bd=1)
        io_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Input
        input_label = tk.Label(io_frame, text="INPUT_SIGNAL", font=("Courier New", 7), 
                              fg=CYAN, bg=PANEL)
        input_label.pack(anchor="w", padx=5, pady=(5, 2))
        
        self.heard_label = tk.Label(
            io_frame,
            textvariable=self.heard_var,
            wraplength=340,
            fg=WHITE,
            bg=PANEL,
            font=("Courier New", 9),
            justify=tk.LEFT
        )
        self.heard_label.pack(anchor="w", padx=5, pady=(0, 5))
        
        # Separator
        sep = tk.Frame(io_frame, bg=CYAN_DIM, height=1)
        sep.pack(fill=tk.X, pady=3)
        
        # Output
        output_label = tk.Label(io_frame, text="FRIDAY_RESPONSE", font=("Courier New", 7), 
                               fg=GREEN, bg=PANEL)
        output_label.pack(anchor="w", padx=5, pady=(5, 2))
        
        self.response_label = tk.Label(
            io_frame,
            textvariable=self.response_var,
            wraplength=340,
            fg=GREEN,
            bg=PANEL,
            font=("Courier New", 9),
            justify=tk.LEFT
        )
        self.response_label.pack(anchor="w", padx=5, pady=(0, 5))
        
        # ===== TELEMETRY LOG =====
        log_label = tk.Label(self.root, text="LIVE_TELEMETRY", font=("Courier New", 7), 
                            fg=DIM, bg=BG)
        log_label.pack(anchor="w", padx=10)
        
        self.log_text = tk.Text(
            self.root,
            height=8,
            width=48,
            bg="#080812",
            fg=CYAN_DIM,
            font=("Courier New", 8),
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # ===== BOTTOM BAR =====
        bottom_frame = tk.Frame(self.root, bg=BG, height=30)
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Time
        self.time_label = tk.Label(
            bottom_frame,
            textvariable=self.time_var,
            font=("Courier New", 9),
            fg=CYAN,
            bg=BG
        )
        self.time_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Status indicator
        self.status_indicator = tk.Label(
            bottom_frame,
            text="● ONLINE",
            font=("Courier New", 8),
            fg=GREEN,
            bg=BG
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=10, pady=5)
    
    def set_status(self, status):
        """Update status and change colors accordingly"""
        def _update():
            self.status_var.set(status)
            
            if status == "LISTENING":
                self.status_label.config(fg=CYAN)
                self.pulse_speed = 3
                self.status_color = CYAN
            elif status == "THINKING":
                self.status_label.config(fg=ORANGE)
                self.pulse_speed = 2
                self.status_color = ORANGE
            elif status == "SPEAKING":
                self.status_label.config(fg=GREEN)
                self.pulse_speed = 2
                self.status_color = GREEN
            elif status in ["PASSIVE", "STANDBY"]:
                self.status_label.config(fg=DIM)
                self.pulse_speed = 1
                self.status_color = DIM
        
        self.root.after(0, _update)
    
    def set_heard(self, text):
        """Update heard text"""
        def _update():
            self.heard_var.set(f"> {text[:70]}")
        
        self.root.after(0, _update)
    
    def set_response(self, text):
        """Update response text"""
        def _update():
            self.response_var.set(text[:180])
        
        self.root.after(0, _update)
    
    def add_log(self, action, result):
        """Add entry to telemetry log"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {action.upper()} → {result[:55]}"
        
        def _insert():
            self._insert_log(entry)
        
        self.root.after(0, _insert)
    
    def _insert_log(self, entry):
        """Insert log entry at top"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(1.0, entry + "\n")
        
        # Keep only last 15 entries
        lines = int(self.log_text.index('end-1c').split('.')[0])
        if lines > 15:
            self.log_text.delete(f"{lines}.0", tk.END)
        
        self.log_text.config(state=tk.DISABLED)
    
    def animate_radar(self):
        """Animate rotating radar scan"""
        try:
            self.radar_canvas.delete("scan_line")
            
            # Draw pulsing circle
            center_x, center_y = 180, 35
            radius = 20
            
            self.radar_canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                outline=self.status_color,
                width=2,
                tags="scan_line"
            )
            
            # Draw rotating scan line
            angle_rad = math.radians(self.scan_angle)
            end_x = center_x + radius * math.cos(angle_rad)
            end_y = center_y + radius * math.sin(angle_rad)
            
            self.radar_canvas.create_line(
                center_x, center_y,
                end_x, end_y,
                fill=self.status_color,
                width=2,
                tags="scan_line"
            )
            
            self.scan_angle = (self.scan_angle + 5) % 360
        except:
            pass
        
        self.root.after(50, self.animate_radar)
    
    def animate_pulse(self):
        """Animate pulsing circle"""
        try:
            if self.pulse_growing:
                self.pulse_radius += self.pulse_speed
                if self.pulse_radius > 30:
                    self.pulse_growing = False
            else:
                self.pulse_radius -= self.pulse_speed
                if self.pulse_radius < 15:
                    self.pulse_growing = True
        except:
            pass
        
        self.root.after(30, self.animate_pulse)
    
    def update_metrics(self):
        """Update system metrics"""
        def _update():
            try:
                cpu = psutil.cpu_percent()
                mem = psutil.virtual_memory().percent
                battery = psutil.sensors_battery()
                
                self.cpu_bar['value'] = cpu
                self.mem_bar['value'] = mem
                
                if battery:
                    self.battery_bar['value'] = battery.percent
                
                self.cpu_var.set(f"CPU: {cpu:.1f}%")
                self.mem_var.set(f"MEM: {mem:.1f}%")
                if battery:
                    self.battery_var.set(f"PWR: {battery.percent:.0f}%")
            except:
                pass
        
        self.root.after(0, _update)
        self.root.after(2000, self.update_metrics)
    
    def update_time(self):
        """Update time display"""
        def _update():
            self.time_var.set(datetime.datetime.now().strftime("%H:%M:%S"))
        
        self.root.after(0, _update)
        self.root.after(1000, self.update_time)
    
    def start_animations(self):
        """Start all animations"""
        self.root.after(100, self.animate_radar)
        self.root.after(100, self.animate_pulse)
        self.root.after(100, self.update_metrics)
        self.root.after(100, self.update_time)
    
    def run(self):
        """Run the dashboard GUI"""
        self.root.mainloop()


# Global dashboard instance
_dashboard = None


def init_dashboard():
    """Initialize the dashboard"""
    global _dashboard
    _dashboard = FridayDashboard()
    return _dashboard


def update_status(status):
    """Update dashboard status"""
    if _dashboard:
        _dashboard.set_status(status)


def update_heard(text):
    """Update heard text"""
    if _dashboard:
        _dashboard.set_heard(text)


def update_response(text):
    """Update response text"""
    if _dashboard:
        _dashboard.set_response(text)


def log_action(action, result):
    """Log an action"""
    if _dashboard:
        _dashboard.add_log(action, result)


def get_dashboard():
    """Get the dashboard instance"""
    return _dashboard
