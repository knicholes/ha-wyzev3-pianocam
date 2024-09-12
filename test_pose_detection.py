# test_pose_detection.py
from logging_config import setup_logging
from config import RTSP_URL
from rtsp_stream import RTSPStream
from pose_detection_service import PoseDetectionService
import logging
import threading

def main():
    setup_logging()
    logger = logging.getLogger('TestPoseDetection')

    if not RTSP_URL:
        logger.error("RTSP_URL must be set in environment variables.")
        return

    rtsp_stream = RTSPStream(RTSP_URL)
    rtsp_stream.start()

    def pose_callback(status):
        logger.info(f"Pose status: {'Person sitting' if status else 'No person detected'}")

    pose_service = PoseDetectionService(rtsp_stream)
    pose_service.set_callback(pose_callback)
    pose_service.start()

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down pose detection service...")
        rtsp_stream.stop()
        pose_service.stop()

if __name__ == "__main__":
    main()
