# pose_detection_service.py
import threading
import logging
import cv2
import mediapipe as mp

class PoseDetectionService:
    def __init__(self, rtsp_stream):
        self.rtsp_stream = rtsp_stream
        self.logger = logging.getLogger(self.__class__.__name__)
        self.person_sitting = False
        self.running = False
        self.callback = None
        self.pose = mp.solutions.pose.Pose(static_image_mode=False, min_detection_confidence=0.5)

    def start(self):
        self.running = True
        threading.Thread(target=self._process_video, daemon=True).start()
        self.logger.info("Pose detection service started.")

    def stop(self):
        self.running = False
        self.logger.info("Pose detection service stopped.")

    def _process_video(self):
        while self.running:
            frame = self.rtsp_stream.get_video_frame()
            if frame is not None:
                is_sitting = self._detect_pose(frame)
                if is_sitting != self.person_sitting:
                    self.person_sitting = is_sitting
                    if self.callback:
                        self.callback(self.person_sitting)
            else:
                self.logger.debug("No video frame received.")
            threading.Event().wait(0.1)  # Adjust as necessary

    def _detect_pose(self, frame):
        try:
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
                left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]
                right_hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

                shoulder_y = (left_shoulder.y + right_shoulder.y) / 2
                hip_y = (left_hip.y + right_hip.y) / 2
                is_sitting = shoulder_y < hip_y
                self.logger.debug(f"Shoulder Y: {shoulder_y}, Hip Y: {hip_y}, Person sitting: {is_sitting}")
                return is_sitting
            else:
                self.logger.debug("No pose landmarks detected.")
                return False
        except Exception as e:
            self.logger.error(f"Error in pose detection: {e}")
            return False

    def set_callback(self, callback):
        self.callback = callback
