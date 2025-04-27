import cv2
import numpy as np
import threading
import win32api
import win32con
import time

# lower_red1 = np.array([0, 120, 70])
# upper_red1 = np.array([10, 255, 255])
# lower_red2 = np.array([170, 120, 70])
# upper_red2 = np.array([180, 255, 255])

lower_green1 = np.array([35, 70, 70])
upper_green1 = np.array([85, 255, 255])


KEY_CODES = {
    'W': 0x57,
    'A': 0x41,
    'S': 0x53,
    'D': 0x44,
}

active_keys = set()

def hold_keys():
    while True:
        for key in KEY_CODES:
            if key in active_keys:
                win32api.keybd_event(KEY_CODES[key], 0, 0, 0)
            else:
                win32api.keybd_event(KEY_CODES[key], 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.05)

threading.Thread(target=hold_keys, daemon=True).start()

cap = cv2.VideoCapture(4)

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    if not ret:
        break

    h, w, _ = frame.shape

    zone_size = 120
    zones = {
        'W': ((int(w / 2 - zone_size / 2), 0), (int(w / 2 + zone_size / 2), int(zone_size * 2.6))),
        'S': ((int(w / 2 - zone_size / 2), h - int(zone_size * 0.5)), (int(w / 2 + zone_size / 2), h)),
        'A': ((0, 0), (int(zone_size * 2.1), h)),
        'D': ((w - int(zone_size * 2.1), 0), (w, h)),
    }

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_green1, upper_green1)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    current_keys = set()

    for cnt in contours:
        if cv2.contourArea(cnt) > 500:
            x, y, w_obj, h_obj = cv2.boundingRect(cnt)
            obj_rect = (x, y, x + w_obj, y + h_obj)

            for key, (pt1, pt2) in zones.items():
                zx1, zy1 = pt1
                zx2, zy2 = pt2

                if not (obj_rect[2] < zx1 or obj_rect[0] > zx2 or obj_rect[3] < zy1 or obj_rect[1] > zy2):
                    current_keys.add(key)

            cv2.rectangle(frame, (x, y), (x + w_obj, y + h_obj), (0, 255, 0), 2)

    active_keys.clear()
    active_keys.update(current_keys)

    for key, (pt1, pt2) in zones.items():
        color = (0, 0, 255) if key in active_keys else (255, 0, 255)
        cv2.rectangle(frame, pt1, pt2, color, 2)
        cv2.putText(frame, key, (pt1[0] + 10, pt1[1] + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

    cv2.imshow('Red Object Tracker', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
