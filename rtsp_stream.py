# rtsp_stream.py
import threading
import logging
import queue
import av

class RTSPStream:
    def __init__(self, url):
        self.url = url
        self.video_queue = queue.Queue(maxsize=10)
        self.audio_queue = queue.Queue(maxsize=50)
        self.running = False
        self.logger = logging.getLogger(self.__class__.__name__)

    def start(self):
        self.running = True
        threading.Thread(target=self._stream, daemon=True).start()
        self.logger.info("RTSP stream started.")

    def stop(self):
        self.running = False
        self.logger.info("RTSP stream stopped.")

    def _stream(self):
        retry_attempts = 0
        while self.running:
            try:
                container = av.open(self.url)
                self.logger.info("Connected to RTSP stream.")
                retry_attempts = 0

                for packet in container.demux():
                    if not self.running:
                        break
                    for frame in packet.decode():
                        if isinstance(frame, av.VideoFrame):
                            self._enqueue_frame(self.video_queue, frame.to_ndarray(format='bgr24'))
                        elif isinstance(frame, av.AudioFrame):
                            self._enqueue_frame(self.audio_queue, frame.to_ndarray())
            except av.AVError as e:
                self.logger.error(f"RTSP stream error: {e}")
                retry_attempts += 1
                if retry_attempts > 5:
                    self.logger.error("Max retry attempts reached. Exiting stream.")
                    self.running = False
                else:
                    self.logger.info(f"Retrying connection in {2 ** retry_attempts} seconds...")
                    threading.Event().wait(2 ** retry_attempts)
            except Exception as e:
                self.logger.exception(f"Unexpected error in RTSP stream: {e}")
                self.running = False

    def _enqueue_frame(self, q, frame):
        if q.full():
            try:
                discarded = q.get_nowait()
                self.logger.debug("Queue full, discarding oldest frame.")
            except queue.Empty:
                pass
        q.put(frame)

    def get_video_frame(self):
        try:
            frame = self.video_queue.get(timeout=1)
            return frame
        except queue.Empty:
            self.logger.debug("No video frame available.")
            return None

    def get_audio_frames(self):
        frames = []
        while not self.audio_queue.empty():
            frames.append(self.audio_queue.get())
        return frames
