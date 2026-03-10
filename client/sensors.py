import grovepi
import time
import math

TEMP_HUMIDITY_PORT = 4
DISTANCE_PORT = 6
DHT_TYPE = 1   # try 1 first, if needed change to 0

def setup_sensors():
    pass

def read_temp_humidity(retries=5):
    for _ in range(retries):
        try:
            temp, humidity = grovepi.dht(TEMP_HUMIDITY_PORT, DHT_TYPE)

            if temp is None or humidity is None:
                time.sleep(1)
                continue

            if isinstance(temp, float) and math.isnan(temp):
                time.sleep(1)
                continue

            if isinstance(humidity, float) and math.isnan(humidity):
                time.sleep(1)
                continue

            return temp, humidity

        except Exception as e:
            print(f"Temp/Humidity read error: {e}")
            time.sleep(1)

    return None, None

def read_distance():
    try:
        distance = grovepi.ultrasonicRead(DISTANCE_PORT)
        return distance
    except Exception as e:
        print(f"Distance read error: {e}")
        return None
