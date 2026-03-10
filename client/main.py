import time
from sensors import *
from alerts import *
from logger import *
from camera import *

THRESHOLD = 50

while True:

    temp,hum = read_temp_humidity()
    dist = read_distance()

    print("Temp:",temp,"Hum:",hum,"Dist:",dist)

    log_event("ambient",
    {"temp":temp,"humidity":hum,"distance":dist})

    if dist != None and dist < THRESHOLD:

        print("INTRUSION DETECTED")

        trigger_alert()

        image = capture()

        log_event("intrusion",
        {"distance":dist,"image":image})

    time.sleep(5)
