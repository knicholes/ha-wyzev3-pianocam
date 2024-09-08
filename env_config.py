import os

def get_rtsp_url():
    return os.getenv("RTSP_URL", "default_rtsp_url")

def get_home_assistant_url():
    return os.getenv("HA_URL", "http://localhost:8123")
