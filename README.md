# Piano Activity Detection System

A Python-based system that processes an RTSP stream to detect whether a child is playing piano and for how long. The system utilizes audio and pose detection services to monitor piano activity and sends updates to Home Assistant. The application is designed following SOLID principles, ensuring modularity, extensibility, and maintainability.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Set Up Environment Variables](#2-set-up-environment-variables)
  - [3. Build and Run the Docker Container](#3-build-and-run-the-docker-container)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Docker Compose](#docker-compose)
- [Usage](#usage)
  - [Running the Main Application](#running-the-main-application)
  - [Testing Detection Services Independently](#testing-detection-services-independently)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Logging and Monitoring](#logging-and-monitoring)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Features

- **Single RTSP Stream Processing**: Efficiently handles audio and video data from a single RTSP stream to prevent bandwidth issues and ensure data freshness.
- **Audio Detection Service**: Detects if a piano is being played using audio analysis.
- **Pose Detection Service**: Determines if someone is sitting at the piano using pose estimation.
- **Home Assistant Integration**: Sends real-time updates to Home Assistant for smart home automation.
- **Modular Design**: Adheres to SOLID principles for easy maintenance and extensibility.
- **Dockerized Deployment**: Simplifies installation and deployment using Docker and Docker Compose.
- **Robust Error Handling**: Includes comprehensive logging and error handling for production readiness.

---

## Prerequisites

- **Hardware**:
  - Wyze camera with RTSP streaming enabled.
- **Software**:
  - [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/) installed on the host machine.
  - [Home Assistant](https://www.home-assistant.io/) instance running and accessible.
- **Credentials**:
  - Home Assistant Long-Lived Access Token (Instructions to generate: https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token).

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/piano-activity-detection.git
cd piano-activity-detection
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory of the project to store your environment variables:

```bash
RTSP_URL=rtsp://username:password@camera_ip_address/stream
HA_URL=http://homeassistant.local:8123
HA_TOKEN=YOUR_LONG_LIVED_ACCESS_TOKEN
```

**Important**: Replace the placeholders with your actual RTSP URL, Home Assistant URL, and token. Ensure that the `.env` file is **not** committed to version control if it contains sensitive information.

### 3. Build and Run the Docker Container

Build the Docker image and run the container using Docker Compose:

```bash
docker-compose build
docker-compose up -d
```

---

## Configuration

### Environment Variables

- **`RTSP_URL`**: The RTSP stream URL from your Wyze camera.
- **`HA_URL`**: The base URL of your Home Assistant instance (e.g., `http://homeassistant.local:8123`).
- **`HA_TOKEN`**: Your Home Assistant Long-Lived Access Token.

Ensure these variables are correctly set in the `.env` file.

### Docker Compose

The `docker-compose.yml` file manages the Docker container and environment variables:

```yaml
version: '3.8'

services:
  piano_detection:
    build: .
    container_name: piano_detection
    restart: unless-stopped
    environment:
      - RTSP_URL=${RTSP_URL}
      - HA_URL=${HA_URL}
      - HA_TOKEN=${HA_TOKEN}
```

---

## Usage

### Running the Main Application

After building and running the Docker container, the application will automatically start processing the RTSP stream and send updates to Home Assistant.

To view the logs:

```bash
docker-compose logs -f
```

### Testing Detection Services Independently

You can test the audio and pose detection services separately using the provided test scripts.

#### Pose Detection Service

```bash
docker exec -it piano_detection python test_pose_detection.py
```

#### Audio Detection Service

```bash
docker exec -it piano_detection python test_audio_detection.py
```

**Note**: Ensure the main application is not running when testing services independently to avoid conflicts.

---

## Project Structure

```
piano-activity-detection/
├── Dockerfile
├── docker-compose.yml
├── .env
├── requirements.txt
├── README.md
├── config.py
├── logging_config.py
├── rtsp_stream.py
├── audio_detection_service.py
├── pose_detection_service.py
├── detection_monitor.py
├── main.py
├── test_pose_detection.py
├── test_audio_detection.py
└── ... (any additional files)
```

- **`config.py`**: Handles configuration and environment variables.
- **`logging_config.py`**: Sets up logging for the application.
- **`rtsp_stream.py`**: Manages RTSP stream reading and demultiplexing.
- **`audio_detection_service.py`**: Contains the audio detection logic.
- **`pose_detection_service.py`**: Contains the pose detection logic.
- **`detection_monitor.py`**: Monitors detection results and communicates with Home Assistant.
- **`main.py`**: Entry point for running the main application.
- **`test_pose_detection.py`**: Script to test pose detection independently.
- **`test_audio_detection.py`**: Script to test audio detection independently.

---

## Dependencies

The application relies on the following Python packages:

- `av`
- `opencv-python-headless`
- `mediapipe`
- `librosa`
- `requests`
- `numpy`

These dependencies are specified in the `requirements.txt` file and are installed during the Docker image build process.

---

## Logging and Monitoring

- **Logging**: The application logs detailed information, including errors and detection statuses, which can be viewed using `docker-compose logs`.
- **Home Assistant**: Detection statuses are sent to Home Assistant and can be integrated into your smart home automation.

---

## Troubleshooting

- **RTSP Stream Issues**:
  - Ensure the RTSP URL is correct and accessible from the Docker container.
  - Check network configurations and firewall settings if the stream is not accessible.
- **Home Assistant Integration**:
  - Verify that the Home Assistant URL and token are correct.
  - Ensure that the `sensor.piano_status` entity is properly configured in Home Assistant.
- **Performance**:
  - Monitor resource usage and adjust buffer sizes or processing intervals in the code if necessary.
  - Consider allocating more resources to the Docker container if you experience performance issues.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Acknowledgments

- **Wyze Cameras**: For providing affordable cameras with RTSP capabilities.
- **Home Assistant**: For enabling seamless smart home integration.
- **OpenAI's ChatGPT**: Assisted in the initial development and design of this application.
- **Community Contributions**: Thanks to the open-source community for the libraries and tools that made this project possible.

---

**Contact Information**

For questions, issues, or contributions, please contact:

- **Name**: Your Name
- **Email**: your.email@example.com
- **GitHub**: [yourusername](https://github.com/yourusername)

---

**Disclaimer**

This application is intended for educational and personal use. Ensure compliance with local laws and regulations regarding audio and video recording and monitoring.

---

