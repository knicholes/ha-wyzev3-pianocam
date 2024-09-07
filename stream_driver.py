import threading
import cv2
import queue
import logging
import ffmpeg
import numpy as np
import subprocess

class StreamDriver:
    def __init__(self, rtsp_url, audio_queue, video_queue):
        self.rtsp_url = rtsp_url
        self.audio_queue = audio_queue
        self.video_queue = video_queue
        self.stop_event = threading.Event()
        self.video_cap = None
        self.audio_process = None

    def start(self):
        logging.info("Starting RTSP stream consumption.")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            self._initialize_streams()

            while not self.stop_event.is_set():
                # Process the video stream (as fast as possible, discard old frames)
                self._process_video()

                # Process the audio stream
                self._process_audio()

        except Exception as e:
            logging.error(f"Error processing RTSP stream: {e}")
        finally:
            self._cleanup_streams()

        if not self.stop_event.is_set():
            time.sleep(5)  # Retry after failure

    def _initialize_streams(self):
        """Initialize video and audio streams."""
        self.video_cap = cv2.VideoCapture(self.rtsp_url)
        if not self.video_cap.isOpened():
            raise ConnectionError(f"Error opening video stream: {self.rtsp_url}")

        self.audio_process = self._start_ffmpeg_audio()

    def _start_ffmpeg_audio(self):
        """Start FFmpeg process for capturing audio stream."""
        return (
            ffmpeg
            .input(self.rtsp_url, fflags='nobuffer', rtsp_transport='tcp')
            .output('pipe:', format='wav')
            .run_async(pipe_stdout=True, pipe_stderr=subprocess.DEVNULL)
        )

    def _process_video(self):
        """Process the video frame (no throttling, keep it fast)."""
        try:
            for _ in range(5):  # Discard older frames
                if not self.video_cap.grab():
                    logging.error("Error grabbing video frame.")
                    return

            # Retrieve the latest frame
            ret, frame = self.video_cap.retrieve()
            if not ret:
                logging.error("Error retrieving video frame.")
                return

            # Add frame to the queue if there's space
            if not self.video_queue.full():
                self.video_queue.put_nowait(frame)
                logging.debug("Added video frame to queue.")
            else:
                logging.warning("Video queue is full, skipping frame.")

        except queue.Full:
            logging.warning("Video queue is full, skipping frame.")

    def _process_audio(self):
        """Process the audio data."""
        try:
            in_bytes = self.audio_process.stdout.read(1024)
            if in_bytes:
                audio_array = np.frombuffer(in_bytes, dtype=np.int16)

                if not self.audio_queue.full():
                    self.audio_queue.put_nowait(audio_array)
                    logging.debug("Added audio data to queue.")
                else:
                    logging.warning("Audio queue is full, skipping audio chunk.")
            else:
                logging.warning("No audio data received, skipping.")

        except Exception as e:
            logging.error(f"Error reading audio data: {e}")

    def _cleanup_streams(self):
        """Clean up video and audio streams."""
        if self.video_cap:
            self.video_cap.release()

        if self.audio_process:
            self.audio_process.terminate()

        logging.info("RTSP stream stopped and resources released.")

    def stop(self):
        """Stop the stream driver."""
        self.stop_event.set()
        logging.info("StreamDriver stop requested.")
