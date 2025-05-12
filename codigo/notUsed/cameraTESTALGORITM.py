import cv2
import numpy as np

def nothing(x):
    pass

# Create trackbars for HSV tuning
cv2.namedWindow("Trackbars")
cv2.createTrackbar("LH", "Trackbars", 0, 180, nothing)
cv2.createTrackbar("LS", "Trackbars", 100, 255, nothing)
cv2.createTrackbar("LV", "Trackbars", 100, 255, nothing)
cv2.createTrackbar("UH", "Trackbars", 10, 180, nothing)
cv2.createTrackbar("US", "Trackbars", 255, 255, nothing)
cv2.createTrackbar("UV", "Trackbars", 255, 255, nothing)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get HSV values from trackbars
    lh = cv2.getTrackbarPos("LH", "Trackbars")
    ls = cv2.getTrackbarPos("LS", "Trackbars")
    lv = cv2.getTrackbarPos("LV", "Trackbars")
    uh = cv2.getTrackbarPos("UH", "Trackbars")
    us = cv2.getTrackbarPos("US", "Trackbars")
    uv = cv2.getTrackbarPos("UV", "Trackbars")

    lower_red = np.array([lh, ls, lv])
    upper_red = np.array([uh, us, uv])

    mask = cv2.inRange(hsv, lower_red, upper_red)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # Optional: Blur and detect circle (same as before)
    blurred = cv2.GaussianBlur(mask, (9, 9), 2)
    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.2, minDist=50,
                                param1=50, param2=30, minRadius=10, maxRadius=100)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
            cv2.rectangle(frame, (i[0]-5, i[1]-5), (i[0]+5, i[1]+5), (0, 128, 255), -1)
            print(f"Red circle detected at x: {i[0]}, y: {i[1]}, radius: {i[2]}")

    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)
    cv2.imshow("Result", result)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
