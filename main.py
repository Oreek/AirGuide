import cv2
import mediapipe as mp
import pyautogui
import time
import pygetwindow as gw

def air_navigation_mode():
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    pyautogui.moveTo(center_x, center_y)
    
    cap = None
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"[Info] Using camera index {i}")
            break

    if not cap or not cap.isOpened():
        print("[Error] Could not access webcam.")
        return

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8)
    mp_drawing = mp.solutions.drawing_utils

    screen_width, screen_height = pyautogui.size()

    prev_y = None
    last_gesture_time = time.time()
    gesture_cooldown = 1.0
    scroll_sensitivity = 100

    thumb_up_start_time = None
    thumb_up_duration = 0.5

    def focus_browser():
        try:
            browser_windows = [
                win for win in gw.getWindowsWithTitle('') if 'Mozilla' in win.title or 'Chrome' in win.title
            ]
            if browser_windows:
                browser_windows[0].activate()
        except Exception:
            print("[Warning] Could not focus browser. Please focus manually.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("[Error] Camera frame not available.")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks, hand_info in zip(results.multi_hand_landmarks, results.multi_handedness):
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                handedness = hand_info.classification[0].label

                index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
                thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
                middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
                ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
                pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

                x, y = int(index_tip.x * screen_width), int(index_tip.y * screen_height)

                if handedness == "Right":
                    pyautogui.moveTo(x, y)

                    if (thumb_tip.y > index_tip.y and
                        middle_tip.y > index_tip.y and
                        ring_tip.y > index_tip.y and
                        pinky_tip.y > index_tip.y):
                        pyautogui.click()

                if prev_y is not None:
                    dy = prev_y - y
                    if abs(dy) > 5:
                        scroll_amount = int(dy // 5 * scroll_sensitivity)
                        pyautogui.scroll(scroll_amount)

                current_time = time.time()
                if current_time - last_gesture_time > gesture_cooldown:
                    thumb_up = thumb_tip.y < thumb_ip.y - 0.05 and thumb_ip.y < thumb_mcp.y - 0.05

                    if thumb_up:
                        if thumb_up_start_time is None:
                            thumb_up_start_time = current_time
                        elif current_time - thumb_up_start_time > thumb_up_duration:
                            last_gesture_time = current_time
                            focus_browser()

                            if handedness == "Left":
                                print("[Gesture] Previous Tab")
                                pyautogui.hotkey("ctrl", "shift", "tab")
                            elif handedness == "Right":
                                print("[Gesture] Next Tab")
                                pyautogui.hotkey("ctrl", "tab")

                            thumb_up_start_time = None
                    else:
                        thumb_up_start_time = None

                prev_y = y

        else:
            print("[Warning] No hand detected!")

        cv2.imshow("Gesture Browser Control", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    air_navigation_mode()
