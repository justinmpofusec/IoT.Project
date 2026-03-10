import json
import time

logfile = "../logs/events.json"

def log_event(event,data):

    entry = {
        "time":time.time(),
        "event":event,
        "data":data
    }

    with open(logfile,"a") as f:
        f.write(json.dumps(entry)+"\n")
