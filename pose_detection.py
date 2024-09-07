from abc import ABC, abstractmethod
import logging
import sys
import time

import cv2
import mediapipe as mp

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout  # Explicitly set the stream to stdout
)

class VideoStream(ABC):
    """
    Abstract base class for a video stream.
    This allows for future extension to handle different video sources.
    """
    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def read_frame(self):
        pass

    @abstractmethod
    def release(self):
        pass


class RTSPStream(VideoStream):
    def __init__(self, url: str, skip_frames=2, rotation_angle=180):
        self.url = url
        self.cap = None
        self.skip_frames = skip_frames  # Number of frames to skip for efficiency
        self.rotation_angle = rotation_angle  # Angle to rotate the frames

    def open(self):
        self.cap = cv2.VideoCapture(self.url)
        if not self.cap.isOpened():
            raise Exception(f"Error: Could not open RTSP stream from {self.url}")
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Try to keep buffer size minimal


    def read_frame(self):
        # Skip frames for better performance
        for _ in range(self.skip_frames):
            ret, frame = self.cap.read()
            if not ret:
                logging.error("Error: Could not read frame from stream")
                return None

        # Rotate the frame if necessary
        if self.rotation_angle == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif self.rotation_angle == 90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif self.rotation_angle == 270:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        return frame
    
    def read_latest_frame(self):
        # Read frames until the buffer is exhausted
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break  # End of stream or error reading frame
        return frame  # Return the most recent frame


    def release(self):
        if self.cap:
            self.cap.release()




class PoseDetector:
    """
    Class to handle pose detection using MediaPipe.
    """
    def __init__(self):
        # Initialize MediaPipe's Pose object with desired parameters
        self.pose = mp.solutions.pose.Pose(static_image_mode=False,
                                           model_complexity=1,
                                           enable_segmentation=False,
                                           min_detection_confidence=0.5,
                                           min_tracking_confidence=0.5)

    def detect_pose(self, image_rgb):
        """
        Detects the pose in the given RGB image.
        Returns a list of landmarks if a pose is detected, or None if no pose is detected.
        """
        # Run pose detection on the image
        results = self.pose.process(image_rgb)

        # Check if pose landmarks were detected
        if results.pose_landmarks:
            return results.pose_landmarks.landmark  # Return the landmarks
        return None


class PianoPlayerDetector:
    """
    High-level class to determine if the child is sitting at the piano.
    This class applies the logic for detecting piano playing behavior.
    """
    def __init__(self, pose_detector: PoseDetector):
        self.pose_detector = pose_detector

    def detect_pose(self, image_rbg):
        return self.is_playing(image_rbg)
    
    def is_sitting_pose(self, image_rgb):
        """
        Simplified check to see if a person is sitting close to the piano.
        """
        # Get the landmarks from the PoseDetector
        landmarks = self.pose_detector.detect_pose(image_rgb)

        if not landmarks:
            logging.debug("No landmarks detected")
            return False

        # Simplified check: Hips should be lower than shoulders (indicating sitting position)
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]
        right_hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

        if left_hip.y > left_shoulder.y and right_hip.y > right_shoulder.y:
            logging.debug("Person is in a seated position")
            return True
        else:
            logging.debug("Person is not seated")
            return False


class PoseDetectionApp:
    def __init__(self, video_stream: VideoStream, piano_player_detector: PianoPlayerDetector):
        self.video_stream = video_stream
        self.piano_player_detector = piano_player_detector
        try:
            self.video_stream.open()
        except Exception as e:
            logging.error(f"Failed to initialize audio stream: {e}")

        logging.info("PoseDetectionApp initialized successfully")

    def run_once(self):
        try:
            # Read one frame from the video stream
            frame = self.video_stream.read_frame()
            frame = cv2.resize(frame, (640, 360))  # Rescale the frame to a lower resolution

            # Convert the frame to RGB format for processing
            image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Use PianoPlayerDetector to check if the pose corresponds to piano playing
            return self.piano_player_detector.is_sitting_pose(image_rgb)

        except Exception as e:
            logging.error(f"Error during pose detection: {e}")
            return False

    def run(self):
        while True:
            if self.run_once():
                print("Piano playing pose detected")
            time.sleep(5)



if __name__ == "__main__":
    rtsp_url = 'rtsp://pianocam:pianocam@192.168.86.35/live'
    rtsp_stream = RTSPStream(rtsp_url)
    pose_detector = PoseDetector()
    piano_player_detector = PianoPlayerDetector(pose_detector)

    app = PoseDetectionApp(rtsp_stream, piano_player_detector)
    app.run()
