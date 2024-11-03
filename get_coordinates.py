import pyautogui
import time

def get_coordinates():
    print("This tool will help you find the correct coordinates.")
    print("You'll have 3 seconds to move your mouse to each position.")
    
    positions = [
        "search box (where you type contact names)",
        "message box (where you type messages)",
        "attach button (clip icon)",
        "last message area"
    ]
    
    coordinates = {}
    
    for position in positions:
        input(f"\nPress Enter, then move mouse to {position}")
        print("Moving mouse in 3 seconds...")
        time.sleep(3)
        x, y = pyautogui.position()
        coordinates[position] = (x, y)
        print(f"Recorded position: ({x}, {y})")
    
    print("\nHere are your coordinates:")
    for pos, coords in coordinates.items():
        print(f"{pos}: {coords}")

if __name__ == "__main__":
    get_coordinates()