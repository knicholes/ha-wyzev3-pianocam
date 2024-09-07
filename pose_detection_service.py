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
        self.last_process_time = 0  # Tracks when the last frame was processed

    def start(self):
        logging.info("Pose Detection service started.")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            while not self.stop_event.is_set():
                try:
                    # Fetch the latest video frame (without blocking)
                    video_frame = self._get_latest_frame()

                    if video_frame is not None:
                        logging.debug("Processing video frame...")

                        # Only add results to the queue once per second
                        if time.time() - self.last_process_time >= 1.0:
                            if self._detect_pose(video_frame):
                                self._add_result_to_queue({'type': 'video', 'status': 'sitting'})
                                logging.debug("Sitting pose detected.")
                            else:
                                self._add_result_to_queue({'type': 'video', 'status': 'not sitting'})
                                logging.debug("No sitting pose detected.")
                            
                            self.last_process_time = time.time()

                    # Sleep briefly to avoid busy-waiting
                    time.sleep(0.05)

                except queue.Empty:
                    logging.debug("Video queue is empty, waiting for data.")
                except Exception as e:
                    logging.error(f"Unexpected error in PoseDetectionService: {e}")
        except Exception as e:
            logging.error(f"PoseDetectionService error: {e}")
        finally:
            logging.info("Pose Detection service stopped.")

    def _get_latest_frame(self):
        """Fetches the most recent frame from the video queue, discarding older ones."""
        try:
            # Discard older frames to ensure we process only the freshest frame
            video_frame = None
            while not self.video_queue.empty():
                video_frame = self.video_queue.get_nowait()

            if video_frame is not None:
                logging.debug("Got the freshest video frame.")
            return video_frame
        except queue.Empty:
            logging.debug("Video queue is empty, no frame to process.")
            return None

    def _add_result_to_queue(self, result):
        """Adds pose detection result to the result queue."""
        try:
            if not self.result_queue.full():
                self.result_queue.put_nowait(result)
                logging.debug("Added result to queue.")
            else:
                logging.warning("Result queue is full, skipping result.")
        except queue.Full:
            logging.warning("Result queue is full, skipping result.")

    def _detect_pose(self, video_frame):
        """Detects the pose from the video frame using MediaPipe."""
        try:
            frame_rgb = cv2.cvtColor(video_frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(frame_rgb)

            if results.pose_landmarks:
                # Simple pose detection logic: Check if the hip is above the shoulder
                shoulder_y = results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER].y
                hip_y = results.pose_landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP].y
                return hip_y > shoulder_y
            return False
        except cv2.error as e:
            logging.error(f"OpenCV error during pose detection: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error in pose detection: {e}")
            return False

    def stop(self):
        self.stop_event.set()
        logging.info("Pose Detection service stop requested.")
