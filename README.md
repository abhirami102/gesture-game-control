# Temple Run Hand Gesture Controller

A computer vision project that lets you control **Temple Run using hand gestures** through a webcam.

The project uses **MediaPipe Hands** to detect hand landmarks, **OpenCV** for webcam processing, and **pynput** to send keyboard arrow-key inputs.

## Features

* Real-time hand tracking
* Single-hand gesture control
* Jump, slide, left, and right movements
* Gesture stability check
* Cooldown system to prevent repeated actions
* Live webcam display with hand landmarks

## Controls

| Gesture           | Action       |
| ----------------- | ------------ |
| Fist              | Slide ↓      |
| Hand pointing up  | Jump ↑       |
| Hand tilted right | Move Right → |
| Hand tilted left  | Move Left ←  |

## Requirements

* Python 3.8+
* Webcam
* Temple Run or any game using arrow keys

### Install Dependencies

```bash
pip install opencv-python mediapipe pynput
```

## Run

```bash
python temple_run_gesture_controller.py
```

Open the game, click inside the game window, and perform the gestures.

Press **ESC** to exit.

## How It Works

```text
Webcam
   ↓
MediaPipe Hand Detection
   ↓
Gesture Detection
   ↓
Stability + Cooldown Check
   ↓
Arrow Key Input
   ↓
Temple Run
```

The hand's finger positions are used to detect a **fist**, while the direction of the hand is calculated using the wrist and middle-finger landmarks to detect **up, left, and right** movements.
