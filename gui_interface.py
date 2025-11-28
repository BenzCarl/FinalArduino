import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta

# Color Scheme - Modern and Accessible
COLORS = {
    'primary': '#2563eb',      # Vibrant blue
    'primary_dark': '#1e40af', # Darker blue for hover
    'secondary': '#10b981',    # Emerald green
    'danger': '#ef4444',       # Red for critical actions
    'warning': '#f59e0b',      # Amber for warnings
    'success': '#10b981',      # Green for success
    'background': '#0f172a',   # Dark slate
    'surface': '#1e293b',      # Surface color
    'surface_light': '#334155', # Lighter surface
    'text': '#f1f5f9',         # Light text
    'text_secondary': '#cbd5e1', # Secondary text
    'border': '#475569',       # Border color
}

# Font Configuration - Professional and Accessible
FONTS = {
    'title': ('Segoe UI', 20, 'bold'),
    'heading': ('Segoe UI', 14, 'bold'),
    'subheading': ('Segoe UI', 12, 'bold'),
    'body': ('Segoe UI', 10),
    'body_bold': ('Segoe UI', 10, 'bold'),
    'small': ('Segoe UI', 9),
    'mono': ('Consolas', 10),
}

class GUIInterface:
    def __init__(self, root, backend):
        self.root = root
        self.backend = backend
        self.setup_gui()
        
        # Register message handler with backend
        self.backend.add_message_handler(self.handle_message)
        
    def setup_gui(self):
        """Setup the graphical user interface with modern design"""
        self.root.title("🌧️ Smart Clothes Protector")
        self.root.geometry("1000x900")
        self.root.configure(bg=COLORS['background'])
        
        # Configure styles for better accessibility
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=COLORS['background'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable container for better UX
        canvas = tk.Canvas(main_frame, bg=COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Title with better styling
        title_label = tk.Label(
            scrollable_frame,
            text="🧥 SMART CLOTHES PROTECTOR",
            font=FONTS['title'],
            bg=COLORS['background'],
            fg=COLORS['primary'],
            pady=10
        )
        title_label.pack(fill=tk.X, pady=(0, 20))
        
        # Status Frame
        status_frame = self._create_section(scrollable_frame, "System Status")
        
        # Status indicators with better layout
        self.connection_status = self._create_status_indicator(status_frame, "Arduino Connection", "Disconnected")
        self.mode_status = self._create_status_indicator(status_frame, "Operation Mode", "Unknown")
        self.cover_status = self._create_status_indicator(status_frame, "Cover Status", "Unknown")
        self.rain_status = self._create_status_indicator(status_frame, "Rain Detection", "Unknown")
        self.delay_status = self._create_status_indicator(status_frame, "Confirmation Delay", "5 seconds")
        self.schedule_status = self._create_status_indicator(status_frame, "Schedule Status", "Not scheduled")
        
        # Scheduling Frame
        schedule_frame = self._create_section(scrollable_frame, "Schedule Cover")
        self._create_schedule_controls(schedule_frame)
        
        # Control Buttons Frame
        control_frame = self._create_section(scrollable_frame, "Manual Control")
        self._create_control_buttons(control_frame)
        
        # Notifications Frame
        notify_frame = self._create_section(scrollable_frame, "Live Notifications")
        
        # Notifications text area with better styling
        self.notify_text = scrolledtext.ScrolledText(
            notify_frame,
            height=12,
            font=FONTS['mono'],
            bg=COLORS['surface'],
            fg=COLORS['text'],
            insertbackground=COLORS['primary'],
            relief=tk.FLAT,
            borderwidth=1
        )
        self.notify_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.notify_text.config(state=tk.DISABLED)
        
        # Bottom buttons frame
        bottom_frame = tk.Frame(scrollable_frame, bg=COLORS['background'])
        bottom_frame.pack(fill=tk.X, pady=(20, 0))
        
        self._create_button(bottom_frame, "🔄 REFRESH STATUS", self.get_status, COLORS['warning']).pack(side=tk.LEFT, padx=5)
        self._create_button(bottom_frame, "🗑️ CLEAR", self.clear_notifications, COLORS['surface_light']).pack(side=tk.LEFT, padx=5)
        self._create_button(bottom_frame, "❌ EXIT", self.quit_app, COLORS['danger']).pack(side=tk.RIGHT, padx=5)
    
    def _create_section(self, parent, title):
        """Create a styled section frame"""
        section = tk.Frame(parent, bg=COLORS['surface'], relief=tk.FLAT, borderwidth=1)
        section.pack(fill=tk.X, pady=(0, 15), padx=0)
        
        # Section header
        header = tk.Label(
            section,
            text=title,
            font=FONTS['heading'],
            bg=COLORS['primary'],
            fg=COLORS['text'],
            pady=10
        )
        header.pack(fill=tk.X)
        
        # Content frame
        content = tk.Frame(section, bg=COLORS['surface'])
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        return content
    
    def _create_status_indicator(self, parent, label, value):
        """Create a styled status indicator"""
        frame = tk.Frame(parent, bg=COLORS['surface'])
        frame.pack(fill=tk.X, pady=8)
        
        lbl = tk.Label(
            frame,
            text=label + ":",
            font=FONTS['body_bold'],
            bg=COLORS['surface'],
            fg=COLORS['text_secondary'],
            width=22,
            anchor='w'
        )
        lbl.pack(side=tk.LEFT, padx=(0, 15))
        
        value_lbl = tk.Label(
            frame,
            text=value,
            font=FONTS['body_bold'],
            bg=COLORS['surface'],
            fg=COLORS['warning'],
            anchor='w'
        )
        value_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        return value_lbl
    
    def _create_schedule_controls(self, parent):
        """Create schedule control widgets"""
        # Time input frame
        time_frame = tk.Frame(parent, bg=COLORS['surface'])
        time_frame.pack(fill=tk.X, pady=(0, 15))
        
        time_label = tk.Label(
            time_frame,
            text="Open Time:",
            font=FONTS['body_bold'],
            bg=COLORS['surface'],
            fg=COLORS['text_secondary']
        )
        time_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.time_hour = tk.Spinbox(
            time_frame,
            from_=0,
            to=23,
            width=4,
            font=FONTS['body'],
            bg=COLORS['surface_light'],
            fg=COLORS['text'],
            format="%02.0f"
        )
        self.time_hour.pack(side=tk.LEFT, padx=2)
        self.time_hour.delete(0, tk.END)
        self.time_hour.insert(0, datetime.now().strftime("%H"))
        
        time_sep = tk.Label(
            time_frame,
            text=":",
            font=FONTS['body_bold'],
            bg=COLORS['surface'],
            fg=COLORS['text']
        )
        time_sep.pack(side=tk.LEFT, padx=2)
        
        self.time_minute = tk.Spinbox(
            time_frame,
            from_=0,
            to=59,
            width=4,
            font=FONTS['body'],
            bg=COLORS['surface_light'],
            fg=COLORS['text'],
            format="%02.0f"
        )
        self.time_minute.pack(side=tk.LEFT, padx=2)
        self.time_minute.delete(0, tk.END)
        self.time_minute.insert(0, datetime.now().strftime("%M"))
        
        # Hours open frame
        hours_frame = tk.Frame(parent, bg=COLORS['surface'])
        hours_frame.pack(fill=tk.X, pady=(0, 15))
        
        hours_label = tk.Label(
            hours_frame,
            text="Hours Open:",
            font=FONTS['body_bold'],
            bg=COLORS['surface'],
            fg=COLORS['text_secondary']
        )
        hours_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.hours_open = tk.Spinbox(
            hours_frame,
            from_=0.5,
            to=24,
            width=6,
            font=FONTS['body'],
            bg=COLORS['surface_light'],
            fg=COLORS['text'],
            increment=0.5,
            format="%.1f"
        )
        self.hours_open.pack(side=tk.LEFT, padx=2)
        self.hours_open.delete(0, tk.END)
        self.hours_open.insert(0, "2.0")
        
        # Schedule buttons frame
        btn_frame = tk.Frame(parent, bg=COLORS['surface'])
        btn_frame.pack(fill=tk.X)
        
        self._create_button(btn_frame, "📅 Set Schedule", self.set_schedule, COLORS['primary']).pack(side=tk.LEFT, padx=5)
        self._create_button(btn_frame, "❌ Cancel", self.cancel_schedule, COLORS['surface_light']).pack(side=tk.LEFT, padx=5)
    
    def _create_control_buttons(self, parent):
        """Create main control buttons"""
        btn_frame = tk.Frame(parent, bg=COLORS['surface'])
        btn_frame.pack(fill=tk.X)
        
        self.btn_close = self._create_button(
            btn_frame,
            "🛑 EMERGENCY CLOSE",
            self.manual_close,
            COLORS['danger'],
            height=3
        )
        self.btn_close.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        self.btn_open = self._create_button(
            btn_frame,
            "☀️ OPEN COVER",
            self.manual_open,
            COLORS['success'],
            height=3
        )
        self.btn_open.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
        
        self.btn_auto = self._create_button(
            btn_frame,
            "🌧️ AUTO RAIN DETECTION",
            self.set_auto,
            COLORS['primary'],
            height=3
        )
        self.btn_auto.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.BOTH, expand=True)
    
    def _create_button(self, parent, text, command, bg_color, height=2):
        """Create a styled button with accessibility features"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=FONTS['body_bold'],
            bg=bg_color,
            fg=COLORS['text'],
            activebackground=bg_color,
            activeforeground=COLORS['text'],
            relief=tk.FLAT,
            borderwidth=0,
            padx=15,
            pady=10,
            height=height,
            cursor="hand2"
        )
        
        # Add hover effect for better UX
        def on_enter(e):
            btn.config(bg=self._lighten_color(bg_color))
        
        def on_leave(e):
            btn.config(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def _lighten_color(self, color):
        """Lighten a hex color for hover effects"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, int(c * 1.15)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
        
    def update_status(self, status_type, value, color="#e74c3c"):
        """Update status indicators"""
        status_map = {
            "Arduino Connection": self.connection_status,
            "Operation Mode": self.mode_status,
            "Cover Status": self.cover_status,
            "Rain Detection": self.rain_status,
            "Confirmation Delay": self.delay_status,
            "Schedule Status": self.schedule_status
        }
        
        if status_type in status_map:
            status_map[status_type].config(text=value, fg=color)
    
    def handle_message(self, message_type, formatted_message, raw_message):
        """Handle messages from backend"""
        # Add to notifications area
        self.add_notification(message_type, formatted_message)
        
        # Process status updates
        if message_type == "STATUS" and ":" in raw_message:
            status_type, status_value = raw_message.split(":", 1)
            self.process_status_update(status_type.strip(), status_value.strip())
        elif "CONFIRMED_RAINING" in raw_message:
            self.update_status("Cover Status", "CLOSED", "#e74c3c")
            self.update_status("Rain Detection", "RAINING", "#e74c3c")
        elif "CONFIRMED_DRY" in raw_message:
            self.update_status("Cover Status", "OPEN", "#2ecc71")
            self.update_status("Rain Detection", "DRY", "#2ecc71")
        elif "MANUAL_OPENED" in raw_message:
            self.update_status("Cover Status", "OPEN", "#2ecc71")
            self.update_status("Operation Mode", "MANUAL", "#f39c12")
        elif "MANUAL_CLOSED" in raw_message:
            self.update_status("Cover Status", "CLOSED", "#e74c3c")
            self.update_status("Operation Mode", "MANUAL", "#f39c12")
        elif "AUTO_MODE" in raw_message:
            self.update_status("Operation Mode", "AUTO", "#3498db")
        elif "Connected" in raw_message and "successfully" in raw_message:
            self.update_status("Arduino Connection", "Connected", "#2ecc71")
            self.update_schedule_status()  # Update schedule status on connect
            self.get_status()
    
    def process_status_update(self, status_type, status_value):
        """Process status updates from Arduino"""
        color = "#e74c3c" if "CLOSED" in status_value or "RAINING" in status_value else "#2ecc71"
        color = "#f39c12" if "MANUAL" in status_value else color
        color = "#3498db" if "AUTO" in status_value else color
        color = "#2ecc71" if "Connected" in status_value else color
        
        self.update_status(status_type, status_value, color)
    
    def add_notification(self, category, message):
        """Add notification to the text area"""
        # Color coding
        colors = {
            "SYSTEM": "#2ecc71",    # Green
            "ARDUINO": "#3498db",   # Blue
            "COMMAND": "#f39c12",   # Orange
            "ERROR": "#e74c3c",     # Red
            "STATUS": "#9b59b6",    # Purple
            "INFO": "#ecf0f1"       # White
        }
        
        color_tag = colors.get(category, "INFO")
        
        self.notify_text.config(state=tk.NORMAL)
        self.notify_text.insert(tk.END, message + "\n", (color_tag,))
        self.notify_text.see(tk.END)
        self.notify_text.config(state=tk.DISABLED)
        
        # Configure tags for colors
        for tag, color in colors.items():
            self.notify_text.tag_configure(tag, foreground=color)
    
    def manual_close(self):
        """Manually close the cover with confirmation modal"""
        if self._show_confirmation_modal(
            "Emergency Close",
            "Are you sure you want to close the cover?\n\nThis is an emergency action.",
            COLORS['danger']
        ):
            if self.backend.manual_close_cover():
                self._show_success_modal("Success", "✓ Cover is closing now")
    
    def manual_open(self):
        """Manually open the cover with confirmation modal"""
        if self._show_confirmation_modal(
            "Open Cover",
            "Are you sure you want to open the cover?\n\nMake sure it's safe to do so.",
            COLORS['success']
        ):
            if self.backend.manual_open_cover():
                self._show_success_modal("Success", "✓ Cover is opening now")
    
    def set_auto(self):
        """Set to automatic mode with confirmation modal"""
        if self._show_confirmation_modal(
            "Auto Mode",
            "Switch to automatic rain detection mode?\n\nThe system will monitor rain and respond automatically.",
            COLORS['primary']
        ):
            if self.backend.set_auto_mode():
                self._show_success_modal("Success", "✓ Switched to automatic mode")
    
    def get_status(self):
        """Get current status from Arduino"""
        self.backend.get_status()
    
    def clear_notifications(self):
        """Clear the notifications area"""
        self.notify_text.config(state=tk.NORMAL)
        self.notify_text.delete(1.0, tk.END)
        self.notify_text.config(state=tk.DISABLED)
        self.add_notification("SYSTEM", "Notifications cleared")
    
    def set_schedule(self):
        """Set schedule for cover opening"""
        if not self.backend.is_connected():
            messagebox.showerror("Connection Error", 
                               "Arduino is not connected. Please check the connection.")
            return
        
        try:
            hour = int(self.time_hour.get())
            minute = int(self.time_minute.get())
            hours_open = float(self.hours_open.get())
            
            # Validate inputs
            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                messagebox.showerror("Invalid Time", "Please enter a valid time (HH:MM)")
                return
            
            if hours_open <= 0 or hours_open > 24:
                messagebox.showerror("Invalid Duration", 
                                   "Hours open must be between 0.5 and 24 hours")
                return
            
            # Create datetime for today with the specified time
            now = datetime.now()
            scheduled_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If the time has already passed today, schedule for tomorrow
            if scheduled_time <= now:
                scheduled_time += timedelta(days=1)
            
            # Set the schedule
            if self.backend.set_schedule(scheduled_time, hours_open):
                self.update_schedule_status()
                
                open_str = scheduled_time.strftime("%H:%M")
                close_time = scheduled_time + timedelta(hours=hours_open)
                close_str = close_time.strftime("%H:%M")
                
                messagebox.showinfo("Schedule Set", 
                                  f"Cover will open at {open_str}\n"
                                  f"and close at {close_str}\n"
                                  f"({hours_open} hours later)")
        except ValueError:
            messagebox.showerror("Invalid Input", 
                               "Please enter valid numbers for time and hours")
    
    def cancel_schedule(self):
        """Cancel the current schedule"""
        if self.backend.cancel_schedule():
            self.update_schedule_status()
            messagebox.showinfo("Schedule Cancelled", "The schedule has been cancelled")
        else:
            messagebox.showinfo("No Schedule", "There is no active schedule to cancel")
    
    def update_schedule_status(self):
        """Update schedule status display"""
        schedule_info = self.backend.get_schedule_info()
        if schedule_info['active']:
            open_str = schedule_info['open_time'].strftime("%H:%M")
            close_str = schedule_info['close_time'].strftime("%H:%M")
            self.update_status("Schedule Status", 
                             f"Open: {open_str}, Close: {close_str}", "#9b59b6")
        else:
            self.update_status("Schedule Status", "Not scheduled", "#bdc3c7")
    
    def quit_app(self):
        """Cleanup and exit"""
        if messagebox.askokcancel("Quit", "Are you sure you want to exit?"):
            self.backend.disconnect()
            self.root.quit()
            self.root.destroy()
    
    def _show_confirmation_modal(self, title, message, color):
        """Show a custom confirmation modal dialog"""
        modal = tk.Toplevel(self.root)
        modal.title(title)
        modal.geometry("400x220")
        modal.resizable(False, False)
        modal.configure(bg=COLORS['background'])
        
        # Center the modal on the parent window
        modal.transient(self.root)
        modal.grab_set()
        
        # Header with color
        header = tk.Frame(modal, bg=color, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header,
            text=title,
            font=FONTS['heading'],
            bg=color,
            fg=COLORS['text']
        )
        title_label.pack(pady=15)
        
        # Message
        msg_frame = tk.Frame(modal, bg=COLORS['background'])
        msg_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        msg_label = tk.Label(
            msg_frame,
            text=message,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text'],
            wraplength=350,
            justify=tk.LEFT
        )
        msg_label.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        btn_frame = tk.Frame(modal, bg=COLORS['background'])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        result = {'confirmed': False}
        
        def confirm():
            result['confirmed'] = True
            modal.destroy()
        
        def cancel():
            modal.destroy()
        
        confirm_btn = tk.Button(
            btn_frame,
            text=" Confirm",
            command=confirm,
            font=FONTS['body_bold'],
            bg=color,
            fg=COLORS['text'],
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        confirm_btn.pack(side=tk.RIGHT, padx=5)
        
        cancel_btn = tk.Button(
            btn_frame,
            text=" Cancel",
            command=cancel,
            font=FONTS['body_bold'],
            bg=COLORS['surface_light'],
            fg=COLORS['text'],
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
        
        # Focus on confirm button and wait
        confirm_btn.focus()
        modal.wait_window()
        
        return result['confirmed']
    
    def _show_success_modal(self, title, message):
        """Show a success modal dialog"""
        modal = tk.Toplevel(self.root)
        modal.title(title)
        modal.geometry("350x180")
        modal.resizable(False, False)
        modal.configure(bg=COLORS['background'])
        
        # Center the modal
        modal.transient(self.root)
        modal.grab_set()
        
        # Header with success color
        header = tk.Frame(modal, bg=COLORS['success'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title_label = tk.Label(
            header,
            text=title,
            font=FONTS['heading'],
            bg=COLORS['success'],
            fg=COLORS['text']
        )
        title_label.pack(pady=10)
        
        # Message
        msg_frame = tk.Frame(modal, bg=COLORS['background'])
        msg_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        msg_label = tk.Label(
            msg_frame,
            text=message,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text'],
            wraplength=300
        )
        msg_label.pack(fill=tk.BOTH, expand=True)
        
        # OK Button
        btn_frame = tk.Frame(modal, bg=COLORS['background'])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        ok_btn = tk.Button(
            btn_frame,
            text="OK",
            command=modal.destroy,
            font=FONTS['body_bold'],
            bg=COLORS['success'],
            fg=COLORS['text'],
            relief=tk.FLAT,
            padx=30,
            pady=8,
            cursor="hand2"
        )
        ok_btn.pack(side=tk.RIGHT)
        ok_btn.focus()
        
        # Auto-close after 3 seconds
        modal.after(3000, modal.destroy)