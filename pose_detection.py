import cv2
import mediapipe as mp

class PoseDetectionApp:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.pose = mp.solutions.pose.Pose()

    def detect_pose(self):
        cap = cv2.VideoCapture(self.rtsp_url)
        ret, frame = cap.read()
        if not ret:
            return False

        results = self.pose.process(frame)

        if results.pose_landmarks:
            return self.is_sitting_at_piano(results.pose_landmarks)
        return False

    def is_sitting_at_piano(self, landmarks):
        # Detect shoulder above waist landmark to check sitting posture
        shoulders_above_waist = landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].y < \
                                landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP].y
        return shoulders_above_waist
