import cv2
import os
import mediapipe as mp
import numpy as np

# ✅ Frame extraction
def extract_frames(video_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"🚫 Failed to open video file for frame extraction: {video_path}")
        return 0

    count = 0
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            break

        frame_filename = os.path.join(output_dir, f'frame_{count:04d}.jpg')
        cv2.imwrite(frame_filename, frame)
        count += 1

    cap.release()
    return count


# ✅ Landmark detection + Behavior analysis
def process_video(input_path, output_path=None):
    mp_drawing = mp.solutions.drawing_utils
    mp_holistic = mp.solutions.holistic

    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"🚫 Failed to open video file: {input_path}")
        return False, {}

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Ensure even dimensions
    width -= width % 2
    height -= height % 2

    if fps == 0 or width == 0 or height == 0:
        print("⚠️ Invalid video metadata (fps/width/height).")
        cap.release()
        return False, {}

    out = None
    if output_path:
        fourcc = cv2.VideoWriter_fourcc(*'X', 'V', 'I', 'D')  # Compatible codec
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    total_frames = 0
    tension_frames = 0  # heuristic: hand near face

    with mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            try:
                # Convert BGR to RGB for MediaPipe
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = holistic.process(image_rgb)
                # Convert back to BGR for drawing/output
                image_bgr = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

                # Draw landmarks if present
                if results.face_landmarks:
                    mp_drawing.draw_landmarks(
                        image_bgr, results.face_landmarks, mp_holistic.FACEMESH_TESSELATION
                    )
                if results.pose_landmarks:
                    mp_drawing.draw_landmarks(
                        image_bgr, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS
                    )
                if results.left_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image_bgr, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS
                    )
                if results.right_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        image_bgr, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS
                    )

                # Behavior heuristic: hand near face (tension)
                hand_near_face = False
                if results.pose_landmarks:
                    nose = results.pose_landmarks.landmark[mp_holistic.PoseLandmark.NOSE]
                    if results.left_hand_landmarks:
                        left_wrist = results.left_hand_landmarks.landmark[0]
                        dist_left = ((nose.x - left_wrist.x) ** 2 + (nose.y - left_wrist.y) ** 2) ** 0.5
                        if dist_left < 0.15:
                            hand_near_face = True
                    if results.right_hand_landmarks:
                        right_wrist = results.right_hand_landmarks.landmark[0]
                        dist_right = ((nose.x - right_wrist.x) ** 2 + (nose.y - right_wrist.y) ** 2) ** 0.5
                        if dist_right < 0.15:
                            hand_near_face = True

                    # Count only when pose landmarks exist
                    total_frames += 1
                    if hand_near_face:
                        tension_frames += 1

                if out:
                    out.write(image_bgr)

            except Exception as e:
                print(f"🚨 Error during frame processing: {e}")
                continue

    cap.release()
    if out:
        out.release()

    tension_ratio = round((tension_frames / total_frames) if total_frames else 0, 2)
    behavior_summary = {
        "total_frames": total_frames,
        "tension_frames": tension_frames,
        "tension_ratio": tension_ratio,
        "interpretation": "Tense" if tension_ratio > 0.2 else "Calm"
    }

    return True, behavior_summary
