import os
import requests

class HomeAssistant:
    def __init__(self, home_assistant_url):
        self.url = home_assistant_url

    def update_playtime(self, is_playing):
        try:
            data = {"is_playing": is_playing}
            response = requests.post(f"{self.url}/api/piano_playtime", json=data)
            if response.status_code != 200:
                print(f"Failed to update Home Assistant: {response.text}")
        except Exception as e:
            print(f"Error in HomeAssistant update: {e}")
