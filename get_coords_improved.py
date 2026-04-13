import pyautogui
import time
import os

print("=" * 70)
print("MOUSE COORDINATE TRACKER (SIMPLE VERSION)")
print("=" * 70)
print()
print("Instructions:")
print("1. Move your mouse to the center of a play button")
print("2. Look at the coordinates shown below")
print("3. Read them slowly and carefully")
print("4. Tell me the button and coordinates")
print()
print("=" * 70)
print()

try:
    last_x, last_y = -1, -1
    print("Move your mouse over the buttons now...\n")
    
    while True:
        x, y = pyautogui.position()
        
        # Only print when position changes significantly (every 5 pixels)
        if abs(x - last_x) > 5 or abs(y - last_y) > 5:
            # Clear screen
            os.system('cls' if os.name == 'nt' else 'clear')
            print("=" * 70)
            print("CURRENT MOUSE POSITION:")
            print("=" * 70)
            print()
            print(f"   X-coordinate: {x}")
            print(f"   Y-coordinate: {y}")
            print()
            print("=" * 70)
            print("(Move your mouse to see updated coordinates)")
            print("(Press Ctrl+C to quit)")
            print("=" * 70)
            
            last_x, last_y = x, y
        
        time.sleep(0.05)
        
except KeyboardInterrupt:
    print("\n\nStopped. Goodbye!")
