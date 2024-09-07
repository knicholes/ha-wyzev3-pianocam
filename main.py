import os
import signal
import time
import logging
import queue
from audio_detection_service import AudioDetectionService
from pose_detection_service import PoseDetectionService
from stream_driver import StreamDriver

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)

def main():
    logging.info("Entered main function...")

    # Check if the RTSP_URL environment variable is set
    rtsp_url = os.getenv('RTSP_URL')
    logging.info(f"RTSP_URL: {rtsp_url}")
    
    if not rtsp_url:
        logging.error("RTSP URL not provided. Exiting.")
        return

    # Use queue.Queue for thread-safe communication between components
    audio_queue = queue.Queue(maxsize=10)  # Audio queue with a max size of 10 items
    video_queue = queue.Queue(maxsize=10)  # Video queue with a max size of 10 items
    result_queue = queue.Queue(maxsize=20)  # Results queue

    # Initialize and start the services
    logging.info("Initializing services...")
    stream_driver = StreamDriver(rtsp_url, audio_queue, video_queue)
    audio_service = AudioDetectionService(audio_queue, result_queue)
    pose_service = PoseDetectionService(video_queue, result_queue)

    stream_driver.start()
    audio_service.start()
    pose_service.start()

    logging.info("Services have been started.")

    # Signal handling for shutdown
    def shutdown(signum, frame):
        logging.info("Received shutdown signal. Shutting down...")
        stream_driver.stop()
        audio_service.stop()
        pose_service.stop()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # Keep the program alive while the services are running
    logging.info("Entering main loop...")
    try:
        while not stream_driver.stop_event.is_set() or not audio_service.stop_event.is_set() or not pose_service.stop_event.is_set():
            time.sleep(1)
    except Exception as e:
        logging.error(f"Error in the main loop: {e}")
    finally:
        logging.info("Exiting main loop.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.fatal(f"Fatal error: {e}")
