from sense_hat import SenseHat
import grovepi
import time

LED_PIN = 2
BUZZER_PIN = 3
ULTRASONIC_PIN = 6

sense = SenseHat()

grovepi.pinMode(LED_PIN, "OUTPUT")
grovepi.pinMode(BUZZER_PIN, "OUTPUT")

while True:
    temp = round(sense.get_temperature(), 2)
    hum = round(sense.get_humidity(), 2)
    pressure = round(sense.get_pressure(), 2)

    gyro = sense.get_gyroscope_raw()
    accel = sense.get_accelerometer_raw()

    try:
        distance = grovepi.ultrasonicRead(ULTRASONIC_PIN)
    except Exception:
        distance = -1

    print("Temperature:", temp)
    print("Humidity:", hum)
    print("Pressure:", pressure)
    print("Gyro:", gyro)
    print("Accel:", accel)
    print("Distance:", distance)
    print("-" * 40)

    if distance != -1 and distance <= 20:
        grovepi.digitalWrite(LED_PIN, 1)
        grovepi.digitalWrite(BUZZER_PIN, 1)
        sense.clear(255, 0, 0)
    else:
        grovepi.digitalWrite(LED_PIN, 0)
        grovepi.digitalWrite(BUZZER_PIN, 0)
        sense.clear()

    time.sleep(2)
