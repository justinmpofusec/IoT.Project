import grovepi
import time

temp_sensor = 4
distance_sensor = 6

def read_temp_humidity():
    try:
        temp, humidity = grovepi.dht(temp_sensor,0)
        return temp, humidity
    except:
        return None, None

def read_distance():
    try:
        dist = grovepi.ultrasonicRead(distance_sensor)
        return dist
    except:
        return None
