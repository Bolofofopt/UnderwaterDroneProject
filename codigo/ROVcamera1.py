from ROV import ROVsensors
from pymavlink import mavutil # type: ignore
import numpy as np
import cv2

sensors = ROVsensors()


master = mavutil.mavlink_connection('udp:0.0.0.0:14550')
master.wait_heartbeat()

def send_velocity(vx, vy, vz, yaw_rate):
    """
    Send velocity commands to the ROV.
    """
    master.mav.set_position_target_local_ned_send(
        0,  # time_boot_ms (not used)
        master.target_system, master.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111,  # type_mask (only control velocity)
        0, 0, 0,  # x, y, z positions (not used)
        vx, vy, vz,  # x, y, z velocity in m/s
        0, 0, 0,  # x, y, z acceleration (not used)
        yaw_rate, 0)  # yaw, yaw_rate

def detect_red_circle(frame):
    """
    Detect a red circle in the frame.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 120, 70])
    upper_red = np.array([10, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red, upper_red)

    lower_red = np.array([170, 120, 70])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(hsv, lower_red, upper_red)

    mask = mask1 + mask2
    blurred = cv2.GaussianBlur(mask, (9, 9), 2)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                                param1=50, param2=30, minRadius=10, maxRadius=100)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        return circles[0]  # Return the first detected circle (x, y, radius)
    return None

# Open the camera feed
cap = cv2.VideoCapture(0)  # Replace 0 with the camera index or URL if needed

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    circle = detect_red_circle(frame)
    if circle is not None:
        x, y, radius = circle
        cv2.circle(frame, (x, y), radius, (0, 255, 0), 2)
        cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        # Calculate offsets from the center of the frame
        height, width, _ = frame.shape
        offset_x = x - width // 2
        offset_y = y - height // 2

        # Adjust ROV movement based on offsets
        vx = -0.01 * offset_y  # Forward/backward
        vy = 0.01 * offset_x   # Left/right
        vz = 0                 # Depth (not used here)
        yaw_rate = 0           # Yaw (not used here)

        send_velocity(vx, vy, vz, yaw_rate)
    else:
        # Stop the ROV if no circle is detected
        send_velocity(0, 0, 0, 0)

    # Display the frame
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()