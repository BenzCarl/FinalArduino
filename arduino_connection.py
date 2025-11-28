import serial
import time
import threading
from datetime import datetime, timedelta

class ArduinoConnection:
    """
    Handles communication with Arduino.
    
    Note: Arduino behavior:
    - Rain detected: Cover closes immediately (no delay)
    - Rain stopped: Cover opens after 5 second delay
    """
    def __init__(self, port='COM8', baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.arduino = None
        self.running = False
        self.serial_thread = None
        self.message_handlers = []
        self.scheduled_open_time = None
        self.scheduled_close_time = None
        self.schedule_active = False
        
    def add_message_handler(self, handler):
        """Add a function to handle incoming messages"""
        self.message_handlers.append(handler)
        
    def connect(self):
        """Connect to Arduino"""
        try:
            self.arduino = serial.Serial(self.port, self.baudrate, timeout=1)
            time.sleep(2)  # Wait for Arduino reset
            self.running = True
            self._notify_handlers("SYSTEM", "✅ Connected to Arduino successfully!")
            self._start_serial_reader()
            return True
        except Exception as e:
            self._notify_handlers("ERROR", f"❌ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from Arduino"""
        self.running = False
        if self.arduino and self.arduino.is_open:
            self.arduino.close()
        self._notify_handlers("SYSTEM", "Disconnected from Arduino")
    
    def send_command(self, command):
        """Send command to Arduino"""
        if self.arduino and self.arduino.is_open:
            try:
                self.arduino.write(f"{command}\n".encode())
                self._notify_handlers("COMMAND", f"📡 Sent: {command}")
                return True
            except Exception as e:
                self._notify_handlers("ERROR", f"Send failed: {e}")
                return False
        return False
    
    def _start_serial_reader(self):
        """Start background thread for reading serial data"""
        def read_serial():
            while self.running:
                if self.arduino and self.arduino.in_waiting > 0:
                    try:
                        message = self.arduino.readline().decode().strip()
                        if message:
                            self._process_arduino_message(message)
                    except Exception as e:
                        self._notify_handlers("ERROR", f"Serial read error: {e}")
                time.sleep(0.1)
        
        self.serial_thread = threading.Thread(target=read_serial, daemon=True)
        self.serial_thread.start()
    
    def _process_arduino_message(self, message):
        """Process incoming messages from Arduino"""
        if message.startswith("NOTIFICATION:"):
            self._notify_handlers("ARDUINO", message[13:])
        elif message.startswith("STATUS:"):
            self._notify_handlers("STATUS", message[7:])
        elif message.startswith("SYSTEM:"):
            self._notify_handlers("SYSTEM", message[7:])
        elif message.startswith("ERROR:"):
            self._notify_handlers("ERROR", message[6:])
        else:
            self._notify_handlers("INFO", message)
    
    def _notify_handlers(self, message_type, message):
        """Notify all registered message handlers"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        for handler in self.message_handlers:
            try:
                handler(message_type, formatted_message, message)
            except Exception as e:
                print(f"Handler error: {e}")
    
    def is_connected(self):
        """Check if Arduino is connected"""
        return self.arduino and self.arduino.is_open
    
    def manual_close_cover(self):
        """Send close cover command"""
        return self.send_command("CLOSE")
    
    def manual_open_cover(self):
        """Send open cover command"""
        return self.send_command("OPEN")
    
    def set_auto_mode(self):
        """Send auto mode command"""
        return self.send_command("AUTO")
    
    def get_status(self):
        """Request status update"""
        return self.send_command("STATUS")
    
    def set_schedule(self, open_time, hours_open):
        """
        Schedule cover to open at a specific time and close after specified hours.
        
        Args:
            open_time: datetime object for when to open the cover
            hours_open: float, number of hours to keep cover open before closing
        """
        if not self.is_connected():
            self._notify_handlers("ERROR", "Cannot schedule: Arduino not connected")
            return False
        
        self.scheduled_open_time = open_time
        self.scheduled_close_time = open_time + timedelta(hours=hours_open)
        self.schedule_active = True
        self._schedule_opened = False  # Reset flags for new schedule
        self._schedule_closed = False
        
        open_str = open_time.strftime("%H:%M:%S")
        close_str = self.scheduled_close_time.strftime("%H:%M:%S")
        
        self._notify_handlers("SYSTEM", 
            f"📅 Schedule set: Open at {open_str}, Close at {close_str} ({hours_open} hours)")
        return True
    
    def cancel_schedule(self):
        """Cancel any active schedule"""
        if self.schedule_active:
            self.schedule_active = False
            self.scheduled_open_time = None
            self.scheduled_close_time = None
            if hasattr(self, '_schedule_opened'):
                delattr(self, '_schedule_opened')
            if hasattr(self, '_schedule_closed'):
                delattr(self, '_schedule_closed')
            self._notify_handlers("SYSTEM", "📅 Schedule cancelled")
            return True
        return False
    
    def get_schedule_info(self):
        """Get current schedule information"""
        if self.schedule_active and self.scheduled_open_time:
            return {
                'active': True,
                'open_time': self.scheduled_open_time,
                'close_time': self.scheduled_close_time,
                'hours_open': (self.scheduled_close_time - self.scheduled_open_time).total_seconds() / 3600
            }
        return {'active': False}
    
    def check_schedule(self):
        """Check if scheduled actions need to be executed. Returns action taken or None."""
        if not self.schedule_active or not self.is_connected():
            return None
        
        now = datetime.now()
        action = None
        
        # Check if it's time to open
        if self.scheduled_open_time and now >= self.scheduled_open_time:
            # Check if we haven't already opened for this schedule
            if not hasattr(self, '_schedule_opened') or not self._schedule_opened:
                if self.manual_open_cover():
                    self._schedule_opened = True
                    action = "OPENED"
                    self._notify_handlers("SYSTEM", 
                        f"⏰ Scheduled open executed at {now.strftime('%H:%M:%S')}")
        
        # Check if it's time to close
        if self.scheduled_close_time and now >= self.scheduled_close_time:
            # Check if we haven't already closed for this schedule
            if not hasattr(self, '_schedule_closed') or not self._schedule_closed:
                if self.manual_close_cover():
                    self._schedule_closed = True
                    action = "CLOSED"
                    self.schedule_active = False  # Schedule completed
                    self._notify_handlers("SYSTEM", 
                        f"⏰ Scheduled close executed at {now.strftime('%H:%M:%S')}")
        
        return action