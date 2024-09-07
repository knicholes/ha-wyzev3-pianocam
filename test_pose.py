import cv2
import mediapipe as mp

def test_pose_detection():
    # Initialize the MediaPipe pose model
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()

    # Simulate a test frame (a plain white image)
    frame = cv2.imread('path_to_some_image.jpg')  # Replace with the path to any image

    # Convert the image to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame with MediaPipe
    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        print("Pose landmarks detected.")
    else:
        print("No pose landmarks detected.")

if __name__ == "__main__":
    test_pose_detection()
