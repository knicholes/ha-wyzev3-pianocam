# main.py
from logging_config import setup_logging
from config import RTSP_URL, HA_URL, HA_TOKEN
from rtsp_stream import RTSPStream
from audio_detection_service import AudioDetectionService
from pose_detection_service import PoseDetectionService
from detection_monitor import DetectionMonitor
import logging
import threading

def main():
    setup_logging()
    logger = logging.getLogger('Main')

    if not RTSP_URL or not HA_URL or not HA_TOKEN:
        logger.error("RTSP_URL, HA_URL, and HA_TOKEN must be set in environment variables.")
        return

    rtsp_stream = RTSPStream(RTSP_URL)
    rtsp_stream.start()

    detection_monitor = DetectionMonitor(HA_URL, HA_TOKEN)
    detection_monitor.start()

    audio_service = AudioDetectionService(rtsp_stream)
    audio_service.set_callback(detection_monitor.update_audio_status)
    audio_service.start()

    pose_service = PoseDetectionService(rtsp_stream)
    pose_service.set_callback(detection_monitor.update_pose_status)
    pose_service.start()

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        rtsp_stream.stop()
        audio_service.stop()
        pose_service.stop()
        detection_monitor.stop()

if __name__ == "__main__":
    main()
