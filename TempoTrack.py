from datetime import time
import sounddevice as sd
import numpy as np
import librosa


# parameters
sample_rate = 44100 # Hz
buffer_duration = 0.01 # seconds
buffer_size = int(buffer_duration * sample_rate) # number of samples per audio block

print("Listening to Music...")
'''
Func: audio_callback
Params:
indata: np array of shape (blocksize, channels) holding the audio samples
frames: int number of frames or samples in the call
status: error/ reporting status message
'''
def audio_callback(in_data, frame_count, time_info, status):
    if status:
        print("Status: %d" % status)

    # get the first channel
    audio = in_data[:,0]

    # skip incomplete buffers
    if len(audio) < buffer_size:
        return

    # Compute the onset envelope, how much audio energy changes overtime
    onset_env = librosa.onset.onset_strength(y=audio, sr=sample_rate)

    # Estimate the song's tempo, BPM on the onset envelope
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sample_rate)
    print("Tempo:", tempo)

    # exact time of each beat
    beat_times = librosa.frames_to_time(beat_frames, sr=sample_rate)

    # Map the beat_times to the system time
    buffer_start_time = time.time() - buffer_duration
    absolute_beat_times = buffer_start_time + beat_times

    # trigger action on each beat detection
    current_time = time.time()
    for beat_time in absolute_beat_times:
        if abs(current_time - beat_time) < 0.05: # 50 ms tolerance
            print("Beat Detected at {current_time} - Action triggered!")
with sd.InputStream(callback=audio_callback, channels=1, samplerate= sample_rate, blocksize=buffer_size) as stream:
    print("Press Ctrl+C to exit")
    try:
        while True:
            sd.sleep(10)
    except KeyboardInterrupt:
        print("Exiting")