import threading
import time
import queue

from absl import logging
import numpy as np
from scipy.fftpack import fft
from scipy.signal.windows import hann

class AudioDetectionService:
    def __init__(self, audio_queue, result_queue, piano_threshold=5000):
        self.audio_queue = audio_queue
        self.result_queue = result_queue
        self.stop_event = threading.Event()
        self.piano_threshold = piano_threshold
        self.last_process_time = 0  # Tracks when the last audio result was sent

    def start(self):
        logging.info("Audio Detection service started.")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            while not self.stop_event.is_set():
                try:
                    # Use blocking get with a timeout to avoid excessive CPU usage
                    audio_data = self.audio_queue.get(timeout=1)

                    # Only add results to the queue once per second
                    if time.time() - self.last_process_time >= 1.0:
                        if self._detect_piano_playing(audio_data):
                            self._add_result_to_queue({'type': 'audio', 'status': 'playing'})
                            logging.debug("Piano detected.")
                        else:
                            self._add_result_to_queue({'type': 'audio', 'status': 'not playing'})
                            logging.debug("No piano detected.")
                        
                        self.last_process_time = time.time()

                except queue.Empty:
                    logging.debug("Audio queue is empty, waiting for data.")
                except queue.Full:
                    logging.warning("Result queue is full, skipping result.")
                time.sleep(0.05)  # Reduce sleep time for better responsiveness
        except Exception as e:
            logging.error(f"AudioDetectionService error: {e}")
        finally:
            logging.info("AudioDetectionService stopped.")

    def _add_result_to_queue(self, result):
        """Adds audio detection result to the result queue."""
        try:
            if not self.result_queue.full():
                self.result_queue.put_nowait(result)
                logging.debug("Added result to queue.")
            else:
                logging.warning("Result queue is full, skipping result.")
        except queue.Full:
            logging.warning("Result queue is full, skipping result.")

    def _detect_piano_playing(self, audio_data):
        try:
            if len(audio_data) == 0:
                logging.error("Received empty audio data.")
                return False

            # Apply a Hann window to reduce spectral leakage
            windowed_audio = audio_data * hann(len(audio_data))

            # Perform a Fourier Transform
            fft_result = fft(windowed_audio)
            sample_rate = 44100  # Assuming a 44100 Hz sample rate
            freqs = np.fft.fftfreq(len(fft_result), 1 / sample_rate)
            magnitude = np.abs(fft_result) / len(audio_data)

            # Only consider positive frequencies
            positive_freq_indices = np.where(freqs > 0)
            freqs = freqs[positive_freq_indices]
            magnitude = magnitude[positive_freq_indices]

            # Define the piano frequency range (27.5 Hz to 4186 Hz)
            min_piano_freq = 27.5
            max_piano_freq = 4186.0
            piano_freq_indices = np.where((freqs >= min_piano_freq) & (freqs <= max_piano_freq))

            if len(piano_freq_indices[0]) == 0:
                logging.debug("No piano frequencies found in audio data.")
                return False

            # Check if any magnitudes within the piano range exceed the threshold
            if np.max(magnitude[piano_freq_indices]) > 0.01:
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"Error in piano detection: {e}")
            return False

    def stop(self):
        self.stop_event.set()
        logging.info("Audio Detection service stop requested.")
