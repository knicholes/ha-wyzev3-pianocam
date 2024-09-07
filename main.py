import queue
import os
from stream_driver import StreamDriver
from audio_detection_service import AudioDetectionService
from pose_detection_service import PoseDetectionService
from monitor import Monitor
import logging

logging.basicConfig(level=logging.INFO)

def main():
    # Read secrets from environment variables or command line arguments
    rtsp_url = os.getenv('RTSP_URL')  # Or use argparse for command-line args

    if not rtsp_url:
        logging.error("RTSP URL not provided.")
        return

    # Create queues for communication
    audio_queue = queue.Queue()
    video_queue = queue.Queue()
    result_queue = queue.Queue()

    # Initialize components
    stream_driver = StreamDriver(rtsp_url, audio_queue, video_queue)
    audio_service = AudioDetectionService(audio_queue, result_queue)
    pose_service = PoseDetectionService(video_queue, result_queue)
    monitor = Monitor(result_queue)

    # Start the system
    stream_driver.start()
    audio_service.start()
    pose_service.start()
    monitor.start()

    try:
        while True:
            pass  # Keep the main thread alive
    except KeyboardInterrupt:
        logging.info("Shutting down services.")
        stream_driver.stop()
        audio_service.stop()
        pose_service.stop()
        monitor.stop()

if __name__ == "__main__":
    main()
