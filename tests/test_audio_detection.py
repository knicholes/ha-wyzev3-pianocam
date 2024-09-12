# test_audio_detection.py
from logging_config import setup_logging
from config import RTSP_URL
from rtsp_stream import RTSPStream
from audio_detection_service import AudioDetectionService
import logging
import threading

def main():
    setup_logging()
    logger = logging.getLogger('TestAudioDetection')

    if not RTSP_URL:
        logger.error("RTSP_URL must be set in environment variables.")
        return

    rtsp_stream = RTSPStream(RTSP_URL)
    rtsp_stream.start()

    def audio_callback(status):
        logger.info(f"Audio status: {'Piano playing' if status else 'No piano playing'}")

    audio_service = AudioDetectionService(rtsp_stream)
    audio_service.set_callback(audio_callback)
    audio_service.start()

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down audio detection service...")
        rtsp_stream.stop()
        audio_service.stop()

if __name__ == "__main__":
    main()
