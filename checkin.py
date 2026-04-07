'''import pyttsx3

engine = pyttsx3.init()
engine.say("If you hear this, your setup isn't completely broken")
engine.runAndWait()'''

try:
    import cv2
    print("PyAudio is installed ✅")
except ImportError:
    print("PyAudio is NOT installed ❌")