import threading
import cv2
import logging
import ffmpeg
import numpy as np
import queue

class StreamDriver:
    def __init__(self, rtsp_url, audio_queue, video_queue):
        self.rtsp_url = rtsp_url
        self.audio_queue = audio_queue
        self.video_queue = video_queue
        self.stop_event = threading.Event()

    def start(self):
        logging.info("Starting RTSP stream consumption.")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            cap = cv2.VideoCapture(self.rtsp_url)
            if not cap.isOpened():
                logging.error(f"Error opening video stream: {self.rtsp_url}")
                return

            audio_process = (
                ffmpeg
                .input(self.rtsp_url)
                .output('pipe:', format='wav')
                .run_async(pipe_stdout=True, pipe_stderr=True)
            )

            while not self.stop_event.is_set():
                ret, frame = cap.read()
                if not ret:
                    logging.error("Error reading video frame.")
                    break

                try:
                    self.video_queue.put_nowait(frame)
                    logging.info("Added video frame to queue.")
                except queue.Full:
                    logging.warning("Video queue is full, skipping frame.")

                in_bytes = audio_process.stdout.read(1024)
                if in_bytes:
                    audio_array = np.frombuffer(in_bytes, dtype=np.int16)
                    try:
                        self.audio_queue.put_nowait(audio_array)
                        logging.info("Added audio data to queue.")
                    except queue.Full:
                        logging.warning("Audio queue is full, skipping audio chunk.")

        except Exception as e:
            logging.error(f"Error processing RTSP stream: {e}")
        finally:
            cap.release()
            audio_process.terminate()
            logging.info("RTSP stream stopped.")

    def stop(self):
        self.stop_event.set()
        logging.info("StreamDriver stop requested.")
