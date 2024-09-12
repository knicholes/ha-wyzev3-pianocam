# audio_detection_service.py
import threading
import logging
import numpy as np
import librosa

class AudioDetectionService:
    def __init__(self, rtsp_stream):
        self.rtsp_stream = rtsp_stream
        self.logger = logging.getLogger(self.__class__.__name__)
        self.piano_playing = False
        self.running = False
        self.callback = None
        self.buffer_duration = 2  # seconds

    def start(self):
        self.running = True
        threading.Thread(target=self._process_audio, daemon=True).start()
        self.logger.info("Audio detection service started.")

    def stop(self):
        self.running = False
        self.logger.info("Audio detection service stopped.")

    def _process_audio(self):
        sample_rate = 44100  # Adjust based on actual sample rate
        buffer_size = int(self.buffer_duration * sample_rate)
        audio_buffer = np.array([], dtype=np.float32)

        while self.running:
            frames = self.rtsp_stream.get_audio_frames()
            if frames:
                for frame in frames:
                    # Convert to mono if necessary
                    if frame.ndim > 1:
                        frame = np.mean(frame, axis=0)
                    audio_buffer = np.concatenate((audio_buffer, frame))
                # Keep the buffer size within the desired duration
                if len(audio_buffer) > buffer_size:
                    audio_buffer = audio_buffer[-buffer_size:]

                if len(audio_buffer) >= buffer_size:
                    is_piano = self._detect_piano(audio_buffer, sample_rate)
                    if is_piano != self.piano_playing:
                        self.piano_playing = is_piano
                        if self.callback:
                            self.callback(self.piano_playing)
            threading.Event().wait(0.5)  # Adjust processing interval as needed

    def _detect_piano(self, audio_data, sr):
        try:
            # Resample if necessary
            if sr != 22050:
                audio_data = librosa.resample(audio_data, orig_sr=sr, target_sr=22050)
                sr = 22050
            # Perform detection (placeholder logic)
            spectral_centroid = librosa.feature.spectral_centroid(y=audio_data, sr=sr)
            mean_centroid = np.mean(spectral_centroid)
            is_piano = 1000 < mean_centroid < 4000
            self.logger.debug(f"Spectral centroid: {mean_centroid}, Piano playing: {is_piano}")
            return is_piano
        except Exception as e:
            self.logger.error(f"Error in piano detection: {e}")
            return False

    def set_callback(self, callback):
        self.callback = callback
