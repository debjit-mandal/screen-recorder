import cv2
import numpy as np
import pyautogui
import sounddevice as sd
import soundfile as sf
import time

# Set the screen recording parameters
SCREEN_SIZE = (1920, 1080)  # Adjust according to your screen resolution
FILENAME = "screen_record.mp4"
FPS = 30.0
FOURCC = cv2.VideoWriter_fourcc(*"mp4v")
SAMPLE_RATE = 44100
CHANNELS = 2
AUDIO_FILENAME = "audio.wav"

# Set the recording region (top left and bottom right coordinates)
TOP_LEFT = (100, 100)
BOTTOM_RIGHT = (800, 600)

# Calculate the recording region size
WIDTH = BOTTOM_RIGHT[0] - TOP_LEFT[0]
HEIGHT = BOTTOM_RIGHT[1] - TOP_LEFT[1]
SCREEN_SIZE = (WIDTH, HEIGHT)

# Set the countdown duration in seconds
COUNTDOWN_DURATION = 5

# Create a video writer object
out = cv2.VideoWriter(FILENAME, FOURCC, FPS, SCREEN_SIZE)

# Initialize the audio recording
audio_frames = []
recording = False

def audio_callback(indata, frames, time, status):
    audio_frames.append(indata.copy())

# Countdown timer before starting the screen recording
def countdown_timer(duration):
    for i in range(duration, 0, -1):
        print(f"Recording starts in {i} seconds...")
        time.sleep(1)

# Progress bar to visualize recording progress
def print_progress(current_frame, total_frames):
    progress = (current_frame / total_frames) * 100
    bar_length = 30
    filled_length = int(bar_length * progress / 100)
    bar = "#" * filled_length + "-" * (bar_length - filled_length)
    print(f"Progress: [{bar}] {progress:.1f}%\r", end="")

# Start the screen recording
try:
    # Start recording audio
    stream = sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=SAMPLE_RATE)
    stream.start()

    # Display countdown timer
    countdown_timer(COUNTDOWN_DURATION)

    # Start recording screen
    total_frames = int(FPS * COUNTDOWN_DURATION)
    current_frame = 0

    while True:
        # Capture the screen region
        img = pyautogui.screenshot(region=(TOP_LEFT[0], TOP_LEFT[1], WIDTH, HEIGHT))

        # Convert the image to a numpy array representation
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # Write the frame to the video file
        out.write(frame)

        # Display the resulting frame
        cv2.imshow("Screen Recorder", frame)

        # Start recording audio once the screen recording starts
        if not recording:
            recording = True
            sd.start()
            print("Screen recording started.")

        # Print recording progress
        print_progress(current_frame, total_frames)
        current_frame += 1

        # Stop recording when 'q' is pressed
        if cv2.waitKey(1) == ord("q"):
            break

        # Break the loop after the specified duration
        if current_frame >= total_frames:
            break

except Exception as e:
    print(f"Error: {e}")

finally:
    # Stop recording audio and screen
    stream.stop()
    out.release()
    cv2.destroyAllWindows()

    # Save the audio to a file
    audio_data = np.vstack(audio_frames)
    sf.write(AUDIO_FILENAME, audio_data, SAMPLE_RATE, CHANNELS)

    print("\nScreen recording saved as", FILENAME)
    print("Audio recording saved as", AUDIO_FILENAME)
