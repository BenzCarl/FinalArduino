import tkinter as tk
import threading
import time
from arduino_connection import ArduinoConnection
from gui_interface import GUIInterface

class ClothesProtectorApp:
    """
    Main application class for Smart Clothes Protector.
    
    Rain detection behavior:
    - Immediate close when rain is detected
    - 5 second delay before opening when rain stops
    
    Scheduling:
    - Schedule cover to open at a specific time
    - Automatically close after specified hours
    """
    def __init__(self):
        self.root = tk.Tk()
        self.backend = ArduinoConnection(port='COM8')  # Your Arduino port
        self.gui = GUIInterface(self.root, self.backend)
        self.running = True
        self.schedule_thread = None
        
    def start_schedule_checker(self):
        """Start background thread to check and execute scheduled tasks"""
        def check_schedule():
            while self.running:
                try:
                    action = self.backend.check_schedule()
                    if action:
                        # Update GUI schedule status
                        self.root.after(0, self.gui.update_schedule_status)
                except Exception as e:
                    print(f"Schedule checker error: {e}")
                time.sleep(1)  # Check every second
        
        self.schedule_thread = threading.Thread(target=check_schedule, daemon=True)
        self.schedule_thread.start()
        
    def run(self):
        """Start the application"""
        try:
            # Connect to Arduino
            if self.backend.connect():
                print("Application started successfully!")
            else:
                print("Failed to connect to Arduino, but GUI will still run.")
            
            # Start schedule checker
            self.start_schedule_checker()
            
            # Start the GUI
            self.root.mainloop()
            
        except Exception as e:
            print(f"Application error: {e}")
        finally:
            # Cleanup
            self.running = False
            self.backend.disconnect()

def main():
    """Main function"""
    app = ClothesProtectorApp()
    app.run()

if __name__ == "__main__":
    main()