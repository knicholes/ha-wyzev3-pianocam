import time
import os
from audio_detection import AudioDetectionApp
from pose_detection import PoseDetectionApp
from home_assistant import HomeAssistant

class DetectionMonitor:
    def __init__(self, rtsp_url, home_assistant_url):
        self.audio_app = AudioDetectionApp(rtsp_url)
        self.pose_app = PoseDetectionApp(rtsp_url)
        self.home_assistant = HomeAssistant(home_assistant_url)
        self.buffer_time = 60  # 1 minute buffer
        self.last_detected = None

    def run(self):
        while True:
            try:
                pose_detected = self.pose_app.detect_pose()
                audio_detected = self.audio_app.detect_piano()
                print("pose_detected: %s" % pose_detected)
                print("audio_detected: %s" % audio_detected)

                if pose_detected and audio_detected:
                    self.last_detected = time.time()

                if self.last_detected and time.time() - self.last_detected <= self.buffer_time:
                    print("Piano is being played.")
                    # self.home_assistant.update_playtime(True)
                else:
                    print("No activity detected.")
                    # self.home_assistant.update_playtime(False)

                time.sleep(0.5)
            except KeyboardInterrupt:
                print("Detection Monitor stopped.")
                break
