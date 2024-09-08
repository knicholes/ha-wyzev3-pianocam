import cv2
import logging

class RTSPStream:
    def __init__(self, url):
        self.url = url
        self.capture = cv2.VideoCapture(self.url)
        if not self.capture.isOpened():
            raise RuntimeError(f"Failed to open RTSP stream: {self.url}")
        logging.info(f"RTSP stream initialized: {self.url}")

    def read_frame(self):
        ret, frame = self.capture.read()
        if not ret:
            logging.error("Failed to read frame from RTSP stream.")
            return None
        return frame
    
    def release(self):
        self.capture.release()
