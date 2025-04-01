import time
import sounddevice as sd
import numpy as np
import librosa


# parameters
sample_rate = 44100 # Hz
buffer_duration = 5 # seconds
buffer_size = int(buffer_duration * sample_rate) # number of samples per audio block

print("Listening to Music...")
'''
Func: audio_callback
Params:
indata: np array of shape (blocksize, channels) holding the audio samples
frames: int number of frames or samples in the call
status: error/ reporting status message
'''
def audio_callback(indata, frames, time_info, status):
    if status:
        print(status)

    audio = indata[:, 0]  # mono channel

    if len(audio) < buffer_size:
        return

    # Compute onset envelope
    onset_env = librosa.onset.onset_strength(y=audio, sr=sample_rate)

    # Estimate tempo & beat frames
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sample_rate)
    print("Tempo:", tempo)

    # Beat times (relative to buffer)
    beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)

    # Map beat times to system time
    buffer_start_time = time.time() - buffer_duration
    absolute_beat_times = buffer_start_time + beat_times

    # Trigger action on beats
    current_time = time.time()
    for beat_time in absolute_beat_times:
        if abs(current_time - beat_time) < 0.05:
            print(f"Beat Detected at {current_time:.2f}s - Action triggered!")
with sd.InputStream(callback=audio_callback, channels=1, samplerate= sample_rate, blocksize=buffer_size) as stream:
    print("Press Ctrl+C to exit")
    try:
        while True:
            sd.sleep(10)
    except KeyboardInterrupt:
        print("Exiting")