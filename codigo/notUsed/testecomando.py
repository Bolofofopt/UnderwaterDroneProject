from inputs import get_gamepad # type: ignore

print("Press buttons on your controller. Press Ctrl+C to stop.")

try:
    while True:
        events = get_gamepad()
        for event in events:
            if event.ev_type == "Key" and event.state == 1:
                print(f"Pressed: {event.code}")
except KeyboardInterrupt:
    print("Done.")
