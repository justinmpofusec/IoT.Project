import time

try:
    from picamera2 import Picamera2
    camera = Picamera2()
    camera.start()
    CAMERA_AVAILABLE = True
except Exception:
    camera = None
    CAMERA_AVAILABLE = False

def capture():
    if not CAMERA_AVAILABLE:
        return "NO_CAMERA_AVAILABLE"

    filename = "../evidence/" + str(int(time.time())) + ".jpg"
    camera.capture_file(filename)
    return filename
