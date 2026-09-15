import cv2
import mediapipe as mp
import time
import math
from pynput.keyboard import Controller, Key

# ============================================================
# TEMPLE RUN - HAND TILT GESTURE CONTROLLER
#
#   FIST              -> SLIDE (down)
#   HAND POINTING UP  -> JUMP (up)
#   HAND TILTED RIGHT -> RIGHT
#   HAND TILTED LEFT  -> LEFT
# ============================================================

# ---------------- Keyboard ----------------

kb = Controller()

def send_key(key):
    """Press and release a keyboard key."""
    keys = {
        "up": Key.up,
        "down": Key.down,
        "left": Key.left,
        "right": Key.right
    }

    k = keys[key]
    kb.press(k)
    time.sleep(0.08)
    kb.release(k)


# ---------------- MediaPipe ----------------

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.6
)


# ---------------- Webcam ----------------

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("[ERROR] Could not open webcam.")
    exit()


# ============================================================
# FIST DETECTION
# ============================================================

def is_fist(hand):
    """
    Returns True if index, middle, ring and pinky are all folded down.
    (Thumb is ignored - it behaves oddly when the hand is tilted.)
    """

    lm = hand.landmark

    finger_pairs = [
        (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_PIP),
        (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
        (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_PIP),
        (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_PIP),
    ]

    for tip, pip in finger_pairs:
        # If a fingertip is above its middle joint, the finger is extended
        # -> not a fist.
        if lm[tip].y < lm[pip].y:
            return False

    return True


# ============================================================
# HAND TILT / DIRECTION
# ============================================================

def get_hand_angle(hand):
    """
    Draws an imaginary line from the wrist to the base of the middle
    finger and returns the angle of that line in degrees.

        90  = hand pointing straight up
         0  = hand pointing straight right
       180  = hand pointing straight left
    """

    lm = hand.landmark

    wrist = lm[mp_hands.HandLandmark.WRIST]
    middle_mcp = lm[mp_hands.HandLandmark.MIDDLE_FINGER_MCP]

    dx = middle_mcp.x - wrist.x
    dy = middle_mcp.y - wrist.y

    # Image y-axis grows downward, so flip it to get a normal angle.
    angle = math.degrees(math.atan2(-dy, dx))

    return angle


# ============================================================
# GESTURE DETECTION
# ============================================================

def detect_gesture(hand):

    # --------------------------------------------------------
    # 1. FIST = SLIDE (checked first, overrides everything)
    # --------------------------------------------------------

    if is_fist(hand):
        return "slide"

    angle = get_hand_angle(hand)

    # --------------------------------------------------------
    # 2. HAND POINTING UP = JUMP
    # --------------------------------------------------------

    if 60 <= angle <= 120:
        return "jump"

    # --------------------------------------------------------
    # 3. HAND TILTED RIGHT = RIGHT
    # --------------------------------------------------------

    if -40 <= angle < 60:
        return "right"

    # --------------------------------------------------------
    # 4. HAND TILTED LEFT = LEFT
    # --------------------------------------------------------

    if 120 < angle <= 220:
        return "left"

    return None


# ============================================================
# SETTINGS
# ============================================================

last_gesture = None
last_action_time = 0

# Prevent the same gesture from triggering continuously
COOLDOWN = 0.45

# A gesture must be seen for this many consecutive frames before it
# actually triggers a key press. This stops "pass-through" gestures -
# e.g. your hand briefly pointing up while tilting toward right -
# from accidentally firing a jump.
STABLE_FRAMES_NEEDED = 4
gesture_streak = None
gesture_streak_count = 0


# ============================================================
# MAIN LOOP
# ============================================================

print()
print("==============================================")
print("     TEMPLE RUN HAND GESTURE CONTROLLER")
print("==============================================")
print()
print("FIST              -> SLIDE")
print("HAND POINTING UP  -> JUMP")
print("HAND TILTED RIGHT -> RIGHT")
print("HAND TILTED LEFT  -> LEFT")
print()
print("Open Temple Run in your browser.")
print("Click inside the game before playing.")
print("Press ESC to quit.")
print()

while True:

    ret, frame = cap.read()

    if not ret:
        print("[ERROR] Could not read webcam.")
        break

    # Mirror webcam
    frame = cv2.flip(frame, 1)

    # Convert to RGB for MediaPipe
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    result = hands.process(rgb)

    gesture = None

    # --------------------------------------------------------
    # Hand detected
    # --------------------------------------------------------

    if result.multi_hand_landmarks:

        hand = result.multi_hand_landmarks[0]

        gesture = detect_gesture(hand)

        # Draw hand skeleton
        mp_draw.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )


    # --------------------------------------------------------
    # Track how many frames in a row we've seen the same gesture
    # --------------------------------------------------------

    if gesture is not None and gesture == gesture_streak:
        gesture_streak_count += 1
    else:
        gesture_streak = gesture
        gesture_streak_count = 1 if gesture is not None else 0

    # --------------------------------------------------------
    # Send keyboard command
    # --------------------------------------------------------

    current_time = time.time()

    if gesture and gesture_streak_count >= STABLE_FRAMES_NEEDED:

        # Only trigger if cooldown has finished
        if current_time - last_action_time > COOLDOWN:

            if gesture == "jump":
                send_key("up")

            elif gesture == "slide":
                send_key("down")

            elif gesture == "left":
                send_key("left")

            elif gesture == "right":
                send_key("right")

            last_gesture = gesture
            last_action_time = current_time

            # Reset the streak so the same gesture must build up
            # again before it can fire a second time.
            gesture_streak_count = 0


    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    cv2.putText(
        frame,
        "TEMPLE RUN GESTURE CONTROL",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    if last_gesture:

        cv2.putText(
            frame,
            "ACTION: " + last_gesture.upper(),
            (20, 85),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0),
            3
        )

    cv2.putText(
        frame,
        "Fist = Slide | Hand up = Jump",
        (20, frame.shape[0] - 45),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        "Tilt hand left/right = Left/Right",
        (20, frame.shape[0] - 15),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.65,
        (255, 255, 255),
        2
    )

    cv2.imshow(
        "Temple Run Gesture Controller",
        frame
    )


    # ESC = exit
    if cv2.waitKey(1) & 0xFF == 27:
        break


# ============================================================
# CLEANUP
# ============================================================

cap.release()
cv2.destroyAllWindows()
hands.close()

print("Controller stopped.")