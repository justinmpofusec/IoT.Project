from picamera2 import Picamera2
import time

camera = Picamera2()
camera.start()

def capture():

    filename = "../evidence/"+str(int(time.time()))+".jpg"

    camera.capture_file(filename)

    return filename
