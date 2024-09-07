import cv2
import mediapipe as mp
import logging
import sys

# Set up logging to write to stdout explicitly
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    stream=sys.stdout  # Explicitly set the stream to stdout
)

def test_pose_detection():
    logging.info("Initializing MediaPipe Pose Detector")
    
    try:
        # Initialize pose detection
        pose = mp.solutions.pose.Pose()
        logging.info("MediaPipe Pose Detector initialized successfully")

        # Test with a sample image or frame from RTSP stream
        cap = cv2.VideoCapture('rtsp://pianocam:pianocam@192.168.86.35/live')
        if not cap.isOpened():
            logging.error("Failed to open RTSP stream")
            return

        ret, frame = cap.read()
        if not ret:
            logging.error("Failed to read frame from RTSP stream")
            return

        logging.info("Running pose detection on a single frame")
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)

        if results.pose_landmarks:
            logging.info("Pose landmarks detected")
        else:
            logging.info("No pose landmarks detected")
            
    except Exception as e:
        logging.error(f"Error occurred during pose detection: {e}")
        raise  # Re-raise the exception to make it more visible

if __name__ == "__main__":
    try:
        test_pose_detection()
    except Exception as e:
        logging.error(f"Unhandled exception in main: {e}")
