import unittest
import numpy as np
import queue
from audio_detection_service import AudioDetectionService

class TestAudioDetectionService(unittest.TestCase):

    def setUp(self):
        # Set up the necessary queues
        self.audio_queue = queue.Queue()
        self.result_queue = queue.Queue()
        # Create an instance of the AudioDetectionService with a lower threshold
        self.audio_service = AudioDetectionService(self.audio_queue, self.result_queue, piano_threshold=100)

    def test_detect_piano_playing_with_piano_data(self):
        # Simulate audio data with frequencies in the piano range (e.g., A4 = 440 Hz)
        sample_rate = 44100
        duration = 1  # 1 second of audio
        t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
        piano_note_freq = 440  # A4 piano note
        audio_data = 1.0 * np.sin(2 * np.pi * piano_note_freq * t)

    def test_detect_piano_playing_with_piano_data_multiple_notes(self):
        # Test detection for multiple piano notes
        sample_rate = 44100
        duration = 1  # 1 second of audio
        
        # Create a list of piano notes to test (A0, C4, A4, C8)
        piano_frequencies = [27.5, 261.63, 440.0, 4186.0]  # A0, C4, A4, C8
        for freq in piano_frequencies:
            with self.subTest(freq=freq):
                t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
                audio_data = 1.0 * np.sin(2 * np.pi * freq * t)
                result = self.audio_service._detect_piano_playing(audio_data)
                self.assertTrue(result, f"Piano note {freq} Hz was not detected.")


        # Test if the service correctly detects the piano note
        result = self.audio_service._detect_piano_playing(audio_data)
        self.assertTrue(result, "The piano note was not detected.")

    def test_detect_piano_playing_with_random_noise(self):
        # Simulate random noise (which should not trigger a piano detection)
        noise_data = np.random.normal(0, 1, 44100)  # 1 second of white noise

        # Test if the service correctly does not detect piano in the noise
        result = self.audio_service._detect_piano_playing(noise_data)
        self.assertFalse(result, "False positive detected piano note in noise.")

    def test_empty_audio_data(self):
        # Test with empty audio data
        result = self.audio_service._detect_piano_playing([])
        self.assertFalse(result, "The function should return False for empty audio data.")

if __name__ == '__main__':
    unittest.main()
