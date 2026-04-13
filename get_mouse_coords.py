import pyautogui
import time

print("=" * 50)
print("MOUSE COORDINATE TRACKER")
print("=" * 50)
print("Move your mouse to the buttons and the coordinates will be shown below.")
print("Press Ctrl+C to stop.")
print("=" * 50)
print()

try:
    last_x, last_y = -1, -1
    while True:
        x, y = pyautogui.position()
        
        # Only print when position changes to avoid spam
        if x != last_x or y != last_y:
            print(f"Current coordinates: X={x}, Y={y}", end='\r')
            last_x, last_y = x, y
        
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print("\n\nStopped. Goodbye!")
