from inputs import get_gamepad # type: ignore
import subprocess
import time

# Replace these with your confirmed codes if different
Y_BUTTON = "BTN_NORTH"
B_BUTTON = "BTN_EAST"
A_BUTTON = "BTN_SOUTH"

# Track button states
button_states = {
    "y": False,
    "b": False,
    "a": False
}

def check_and_run():
    if all(button_states.values()):
        print("Y + B + A pressed! Running script...")
        subprocess.run(["py", "ANALISEPARAFILTRO.py"])  # Replace with your script path
        time.sleep(1)  # Debounce

print("Listening for Y + B + A combo... (Ctrl+C to stop)")

try:
    while True:
        events = get_gamepad()
        for event in events:
            if event.code == Y_BUTTON:
                button_states["y"] = (event.state == 1)
            elif event.code == B_BUTTON:
                button_states["b"] = (event.state == 1)
            elif event.code == A_BUTTON:
                button_states["a"] = (event.state == 1)

        check_and_run()

except KeyboardInterrupt:
    print("Stopped.")
