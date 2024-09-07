

Docker containers:

## Saving the audio from the stream with ffmpeg.
docker run -d \
  --name ffmpeg-piano-audio \
  -v /mnt/photogrammetry/pianocam/ffmpeg_outputs:/ffmpeg_outputs \
  jrottenberg/ffmpeg:latest \
  ffmpeg -i rtsp://pianocam:pianocam@192.168.86.35/live \
  -vn -acodec copy -t 2400 -y /ffmpeg_outputs/piano_audio.aac

