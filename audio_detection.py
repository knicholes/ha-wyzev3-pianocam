from abc import ABC, abstractmethod
from io import BytesIO
import logging
import subprocess
import time

from pydub import AudioSegment

class AudioStream(ABC):
    """
    Abstract base class for an audio stream.
    This allows flexibility for different types of audio input sources.
    """
    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def read_chunk(self):
        pass

    @abstractmethod
    def release(self):
        pass


class FFmpegAudioStream(AudioStream):
    def __init__(self, rtsp_url: str):
        self.rtsp_url = rtsp_url
        self.process = None

def open(self):
    logging.info(f"Opening audio stream from {self.rtsp_url}")
    try:
        self.process = subprocess.Popen([
            'ffmpeg', '-i', self.rtsp_url,
            '-vn',  # No video
            '-f', 'wav',  # Output format as WAV
            '-ac', '1',  # Single audio channel
            '-ar', '16000',  # Sample rate of 16kHz
            'pipe:1'  # Pipe the output to stdout
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if self.process and self.process.stdout:
            logging.info(f"Audio stream opened successfully from {self.rtsp_url}")
        else:
            logging.error(f"Failed to open audio stream from {self.rtsp_url}")

    except Exception as e:
        stderr_output = self.process.stderr.read() if self.process.stderr else None
        logging.error(f"Failed to open FFmpeg process: {e}, stderr: {stderr_output}")


    def read_chunk(self, chunk_size=4096):
        if not self.process or self.process.stdout is None:
            logging.error("Audio stream not opened.")
            raise Exception("Audio stream not opened.")

        try:
            return self.process.stdout.read(chunk_size)
        except Exception as e:
            logging.error(f"Error reading audio chunk: {e}")
            return None

    def release(self):
        if self.process:
            logging.info("Terminating audio stream")
            self.process.terminate()
            logging.info(f"Audio stream terminated for {self.rtsp_url}")




class PianoSoundDetector:
    """
    Class responsible for detecting piano sound from an audio stream using PyDub.
    """
    def __init__(self, silence_threshold=-40):
        self.silence_threshold = silence_threshold

    def detect_sound(self, audio_chunk) -> bool:
        try:
            # Convert raw audio chunk into an AudioSegment for analysis
            audio_segment = AudioSegment.from_raw(BytesIO(audio_chunk), sample_width=2, frame_rate=16000, channels=1)
            # If the audio segment is louder than the threshold, consider it as piano sound
            if audio_segment.dBFS > self.silence_threshold:
                return True
        except Exception as e:
            print(f"Error detecting sound: {e}")
        return False


class AudioDetectionApp:
    def __init__(self, audio_stream: AudioStream, sound_detector: PianoSoundDetector, buffer_time=60):
        self.audio_stream = audio_stream
        self.sound_detector = sound_detector
        self.buffer_time = buffer_time  # Buffer time for short breaks (e.g., page turns)
        self.playing_time = 0  # Total playing time in seconds
        self.start_time = None
        self.last_detected = time.time()  # Last time sound was detected
        try:
            self.audio_stream.open()
        except Exception as e:
            logging.error(f"Failed to initialize audio stream: {e}")
        logging.info("AudioDetectionApp initialized")

    def run_once(self):
        logging.debug("Running one cycle of audio detection")
        try:
            # Read a chunk of audio data
            audio_chunk = self.audio_stream.read_chunk()
            if audio_chunk is None:
                logging.debug("No audio chunk read")
                return False  # No audio data to process

            # Perform sound detection on the audio chunk
            is_sound_detected = self.sound_detector.detect_sound(audio_chunk)
            if is_sound_detected:
                self.last_detected = time.time()
                self.start_timer()
                logging.debug("sound detected")
                return True  # Sound detected
            elif time.time() - self.last_detected > self.buffer_time:
                self.stop_timer()
                logging.debug("no sound detected")
                return False  # No sound detected

        except Exception as e:
            logging.error(f"Error during audio detection: {e}")
            return False

    def start_timer(self):
        if self.start_time is None:
            self.start_time = time.time()

    def stop_timer(self):
        if self.start_time is not None:
            self.playing_time += time.time() - self.start_time
            self.start_time = None

    def run(self):
        while True:
            self.run_once()
            time.sleep(1)



if __name__ == "__main__":
    # Use the RTSP URL for the Wyze V3 camera
    rtsp_url = 'rtsp://pianocam:pianocam@192.168.86.35/live'
    audio_stream = FFmpegAudioStream(rtsp_url)
    sound_detector = PianoSoundDetector(silence_threshold=-40)

    # Create and run the main audio detection app
    app = AudioDetectionApp(audio_stream, sound_detector, buffer_time=60)
    app.run()
