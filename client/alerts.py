import grovepi
import time

LED = 2
BUZZER = 3

grovepi.pinMode(LED,"OUTPUT")
grovepi.pinMode(BUZZER,"OUTPUT")

def trigger_alert():

    grovepi.digitalWrite(LED,1)
    grovepi.digitalWrite(BUZZER,1)

    time.sleep(2)

    grovepi.digitalWrite(LED,0)
    grovepi.digitalWrite(BUZZER,0)
