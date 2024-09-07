import logging
import threading
import time
import signal
import sys
import queue

from audio_detection import AudioDetectionApp, FFmpegAudioStream, PianoSoundDetector
from pose_detection import PoseDetectionApp, PoseDetector, RTSPStream, PianoPlayerDetector

import requests

# Set up logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    stream=sys.stdout  # Explicitly set the stream to stdout
)


# Detection Manager to combine AudioDetectionApp and PoseDetectionApp
class PianoDetectionManager:
    def __init__(self, audio_app, pose_app, ha_access_token, ha_ip):
        self.audio_app = audio_app
        self.pose_app = pose_app
        self.ha_access_token = ha_access_token
        self.ha_ip = ha_ip
        self.is_running = True
        self.playing_time = 0
        self.start_time = None
        self.audio_detected = False
        self.pose_detected = False

    def audio_detection_worker(self):
        while self.is_running:
            self.audio_detected = self.audio_app.run_once()
            time.sleep(1)

    def pose_detection_worker(self):
        while self.is_running:
            self.pose_detected = self.pose_app.run_once()
            time.sleep(1)

    def monitor_piano_playing(self):
        while self.is_running:
            # If both audio and pose are detected
            if self.audio_detected and self.pose_detected:
                self.start_timer()
                logging.info("Piano playing detected")
            else:
                self.stop_timer()

            # Send updated playing time to Home Assistant
            playing_time_minutes = self.playing_time / 60
            self.send_playing_time_to_home_assistant(playing_time_minutes)

            time.sleep(1)

    def start_timer(self):
        if self.start_time is None:
            self.start_time = time.time()

    def stop_timer(self):
        if self.start_time is not None:
            self.playing_time += time.time() - self.start_time
            self.start_time = None

    def send_playing_time_to_home_assistant(self, playing_time):
        url = f"http://{self.ha_ip}:8123/api/states/input_number.piano_playing_time"
        headers = {
            "Authorization": f"Bearer {self.ha_access_token}",
            "content-type": "application/json"
        }
        data = {"state": playing_time}
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                logging.info(f"Updated Home Assistant with {playing_time:.2f} minutes.")
            else:
                logging.error(f"Error updating Home Assistant: {response.status_code}, {response.text}")
        except Exception as e:
            logging.error(f"Failed to send data to Home Assistant: {e}")

    def run(self):
        audio_thread = threading.Thread(target=self.audio_detection_worker)
        pose_thread = threading.Thread(target=self.pose_detection_worker)

        audio_thread.start()
        pose_thread.start()

        try:
            self.monitor_piano_playing()
        except KeyboardInterrupt:
            self.is_running = False

        audio_thread.join()
        pose_thread.join()



# Assuming the necessary stream and detection objects are instantiated below
if __name__ == "__main__":
    # Setup audio and video streams and detectors
    rtsp_url = 'rtsp://pianocam:pianocam@192.168.86.35/live'
    ha_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyM2YzNTFjMzBlNWM0NDU3OTYzNTdkZGEwMDBkMGVhYyIsImlhdCI6MTcyNTQ5MzE3NiwiZXhwIjoyMDQwODUzMTc2fQ.isuch5sAq3RG3hChOdXBCRW1ufRciNjTFI1jNL2pmOQ"
    ha_ip = "192.168.86.21"
    
    # Audio setup
    audio_stream = FFmpegAudioStream(rtsp_url)
    sound_detector = PianoSoundDetector(silence_threshold=-40)
    audio_app = AudioDetectionApp(audio_stream, sound_detector, buffer_time=60)

    # Pose setup
    video_stream = RTSPStream(rtsp_url)   
    pose_detector = PoseDetector()
    piano_player_detector = PianoPlayerDetector(pose_detector)
    pose_app = PoseDetectionApp(video_stream, piano_player_detector)

    # Combine both detection apps into the detection manager
    detection_manager = PianoDetectionManager(audio_app, pose_app, ha_access_token, ha_ip)
    detection_manager.run()
