import os
from detection_monitor import DetectionMonitor

if __name__ == "__main__":
    rtsp_url = os.getenv("RTSP_URL")
    ha_url = os.getenv("HA_URL")

    if not rtsp_url or not ha_url:
        print("RTSP_URL or HA_URL environment variables not set.")
        exit(1)

    monitor = DetectionMonitor(rtsp_url, ha_url)
    monitor.run()
