import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

def record_audio(filename="input.wav", fs=44100):
    print("Press Enter to start recording")
    input()

    print("Recording... Press Enter to stop")
    recording = []

    def callback(indata, frames, time, status):
        if status:
            print(f"SoundDevice status: {status}")
        recording.append(indata.copy())

    try:
        with sd.InputStream(samplerate=fs, channels=1, callback=callback):
            input()  # wait for user to press Enter again

        if len(recording) == 0:
            print("No audio captured. Did you allow microphone access?")
            return

        audio = np.concatenate(recording, axis=0)
        write(filename, fs, audio)

        print("Recording saved")
    except Exception as e:
        print(f"Error recording audio: {e}. Please check microphone and sounddevice installation.")


if __name__ == '__main__':
    record_audio()
    