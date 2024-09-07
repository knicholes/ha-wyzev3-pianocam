import threading
import time
import cv2
import mediapipe as mp
import queue
from absl import logging

class PoseDetectionService:
    def __init__(self, video_queue, result_queue):
        self.video_queue = video_queue
        self.result_queue = result_queue
        self.stop_event = threading.Event()
        self.pose = mp.solutions.pose.Pose()

    def start(self):
        logging.info("Starting Pose Detection service...")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            while not self.stop_event.is_set():
                try:
                    video_frame = self.video_queue.get_nowait()  # Non-blocking get
                    logging.info("Processing video frame...")

                    if self._detect_pose(video_frame):
                        self.result_queue.put_nowait({'type': 'video', 'status': 'sitting'})  # Non-blocking put
                        logging.info("Sitting pose detected.")
                    else:
                        self.result_queue.put_nowait({'type': 'video', 'status': 'not sitting'})  # Non-blocking put
                        logging.info("No sitting pose detected.")
                except queue.Empty:
                    logging.warning("Video queue is empty, waiting for data.")
                except queue.Full:
                    logging.warning("Result queue is full, skipping result.")
                time.sleep(0.1)
        except Exception as e:
            logging.error(f"PoseDetectionService error: {e}")
        finally:
            logging.info("PoseDetectionService stopped.")

    def _detect_pose(self, video_frame):
        try:
            frame_rgb = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)

            if results.pose_landmarks:
                shoulder_y = results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].y
                hip_y = results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP].y
                return hip_y > shoulder_y
            return False
        except Exception as e:
            logging.error(f"Error in pose detection: {e}")
            return False

    def stop(self):
        self.stop_event.set()
        logging.info("PoseDetectionService stop requested.")
