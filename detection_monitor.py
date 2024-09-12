# detection_monitor.py
import threading
import logging
import requests

class DetectionMonitor:
    def __init__(self, ha_url, ha_token):
        self.ha_url = ha_url
        self.ha_token = ha_token
        self.logger = logging.getLogger(self.__class__.__name__)
        self.audio_status = False
        self.pose_status = False
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._monitor, daemon=True).start()
        self.logger.info("Detection monitor started.")

    def stop(self):
        self.running = False
        self.logger.info("Detection monitor stopped.")

    def update_audio_status(self, status):
        self.audio_status = status
        self.logger.info(f"Audio status updated: {'Piano playing' if status else 'No piano playing'}")

    def update_pose_status(self, status):
        self.pose_status = status
        self.logger.info(f"Pose status updated: {'Person sitting' if status else 'No person detected'}")

    def _monitor(self):
        previous_status = None
        while self.running:
            status = self._determine_status()
            if status != previous_status:
                self._send_status_to_home_assistant(status)
                previous_status = status
            threading.Event().wait(1)

    def _determine_status(self):
        if self.audio_status and self.pose_status:
            return 'playing_piano'
        elif self.pose_status:
            return 'sitting_at_piano'
        else:
            return 'not_at_piano'

    def _send_status_to_home_assistant(self, status):
        try:
            url = f"{self.ha_url}/api/states/sensor.piano_status"
            headers = {
                'Authorization': f'Bearer {self.ha_token}',
                'Content-Type': 'application/json',
            }
            data = {
                "state": status,
                "attributes": {
                    "friendly_name": "Piano Status",
                }
            }
            response = requests.post(url, headers=headers, json=data)
            if response.status_code in (200, 201):
                self.logger.info(f"Status '{status}' sent to Home Assistant.")
            else:
                self.logger.error(f"Failed to send status to Home Assistant: {response.status_code} {response.text}")
        except Exception as e:
            self.logger.error(f"Error sending status to Home Assistant: {e}")
