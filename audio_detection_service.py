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
        self.piano_threshold = piano_threshold  # Ensure a threshold is provided

    def start(self):
        logging.info("Starting Audio Detection service...")
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            while not self.stop_event.is_set():
                try:
                    # Use blocking get with a timeout to avoid excessive CPU usage
                    audio_data = self.audio_queue.get(timeout=1)
                    logging.info("Processing audio data...")
                    if self._detect_piano_playing(audio_data):
                        self.result_queue.put({'type': 'audio', 'status': 'playing'}, timeout=1)  # Blocking put with timeout
                        logging.info("Piano detected.")
                    else:
                        self.result_queue.put({'type': 'audio', 'status': 'not playing'}, timeout=1)
                        logging.debug("No piano detected.")  # Changed to debug to reduce log spam
                except queue.Empty:
                    logging.debug("Audio queue is empty, waiting for data.")
                except queue.Full:
                    logging.warning("Result queue is full, skipping result.")
                time.sleep(0.05)  # Reduced sleep time to make it more responsive
        except Exception as e:
            logging.error(f"AudioDetectionService error: {e}")
        finally:
            logging.info("AudioDetectionService stopped.")

    def _detect_piano_playing(self, audio_data):
        try:
            # Ensure audio_data is not empty
            if len(audio_data) == 0:
                logging.error("Empty audio data received.")
                return False

            # Apply a Hann window to reduce spectral leakage
            windowed_audio = audio_data * hann(len(audio_data))

            # Perform a Fourier Transform on the windowed audio data
            fft_result = fft(windowed_audio)
            sample_rate = 44100  # Assuming 44100 Hz sample rate
            freqs = np.fft.fftfreq(len(fft_result), 1 / sample_rate)

            # Calculate the magnitude of the FFT and normalize it by the length of the audio data
            magnitude = np.abs(fft_result) / len(audio_data)

            # Only consider positive frequencies (the result is symmetric around zero)
            positive_freq_indices = np.where(freqs > 0)
            freqs = freqs[positive_freq_indices]
            magnitude = magnitude[positive_freq_indices]

            # Define the frequency range for piano notes (from ~27.5 Hz (A0) to ~4186 Hz (C8))
            min_piano_freq = 27.5
            max_piano_freq = 4186.0

            # Filter frequencies within the full piano range
            piano_freq_indices = np.where((freqs >= min_piano_freq) & (freqs <= max_piano_freq))

            # If no frequencies are found in the piano range, return False
            if len(piano_freq_indices[0]) == 0:
                logging.warning("No piano frequency components found in audio data.")
                return False

            # Log the frequencies and their magnitudes in the piano range for debugging
            logging.info(f"Detected piano frequencies: {freqs[piano_freq_indices]}")
            logging.info(f"Piano magnitudes: {magnitude[piano_freq_indices]}")

            # Check if there are significant peaks in the magnitude of the FFT within the piano range
            # A threshold of 0.01 is used, but this can be tuned based on your data
            if np.max(magnitude[piano_freq_indices]) > 0.01:
                logging.info("Piano detected in audio signal.")
                return True
            else:
                logging.info("No piano detected in audio signal.")
                return False
        except Exception as e:
            logging.error(f"Error in piano detection: {e}")
            return False


    def stop(self):
        self.stop_event.set()
        logging.info("AudioDetectionService stop requested.")
