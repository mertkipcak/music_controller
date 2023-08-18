import mediapipe as mp
import cv2

import mac_io

# GLOBALS
LAST_GESTURE = None
LAST_GESTURES = [None] * 5

# Volume Globals
VOLUME_MODE = False
BASE_LEVEL = 0


def update_gestures(current_gesture):
    global LAST_GESTURE, LAST_GESTURES
    if current_gesture != LAST_GESTURE and current_gesture != 'None':
        LAST_GESTURE = current_gesture
        LAST_GESTURES.append(current_gesture)
        LAST_GESTURES.pop(0)  # Maintain a window of the last 5 gestures
        return True
    else:
        return False


def process_gestures(result: 'GestureRecognizerResult', output_image: mp.Image, timestamp_ms: int):
    global LAST_GESTURE, LAST_GESTURES, VOLUME_MODE, BASE_LEVEL

    if len(result.gestures) == 0:
        return

    current_gesture = result.gestures[0][0].category_name
    changed = update_gestures(current_gesture)
    print(str(LAST_GESTURES) + " Volume mode: " + str(VOLUME_MODE))
    if VOLUME_MODE and timestamp_ms % 10 == 0:
        mac_io.set_volume(100 - int(result.hand_landmarks[0][8].y * 100))
        # print(100 - int(result.hand_landmarks[0][0].y * 100))

    if LAST_GESTURES[-2] == 'Victory' and 'Pointing_Up' == LAST_GESTURES[-1] and changed:
        # print('success')
        mac_io.toggle_play_pause_spotify()
    elif LAST_GESTURES[-2] == 'Victory' and 'Thumb_Up' == LAST_GESTURES[-1] and changed:
        VOLUME_MODE = not VOLUME_MODE
        # print(f"Volume mode is set to {VOLUME_MODE}")
        BASE_LEVEL = result.hand_landmarks[0][0].y
    elif LAST_GESTURES[-2] == 'ILoveYou' and 'Victory' == LAST_GESTURES[-1] and changed:
        # print('success')
        mac_io.next_track_spotify()
    elif LAST_GESTURES[-2] == 'ILoveYou' and 'Pointing_Up' == LAST_GESTURES[-1] and changed:
        # print('success')
        mac_io.previous_track_spotify()


if __name__ == '__main__':
    BaseOptions = mp.tasks.BaseOptions
    GestureRecognizer = mp.tasks.vision.GestureRecognizer
    GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
    GestureRecognizerResult = mp.tasks.vision.GestureRecognizerResult
    VisionRunningMode = mp.tasks.vision.RunningMode

    video = cv2.VideoCapture(0)

    options = GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_path='gesture_recognizer.task'),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=process_gestures,
        num_hands=5
    )

    timestamp = 0
    with GestureRecognizer.create_from_options(options) as recognizer:
        while video.isOpened():
            ret, frame = video.read()

            if not ret:
                print("Ignoring empty frame")
                break

            frame = cv2.flip(frame, 1)

            timestamp += 1
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            # Send live image data to perform gesture recognition
            # The results are accessible via the `result_callback` provided in
            # the `GestureRecognizerOptions` object.
            # The gesture recognizer must be created with the live stream mode.
            # print(f"Volume: {mac_io.get_volume()}")
            recognizer.recognize_async(mp_image, timestamp)
            # cv2.imshow('Camera', frame)

    video.release()
    cv2.destroyAllWindows()
