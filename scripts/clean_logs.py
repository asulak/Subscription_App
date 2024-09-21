# scripts/clean_logs.py

import os
import datetime

LOG_DIRECTORY = '/path/to/logs'
DAYS_TO_KEEP = 30

now = datetime.datetime.now()
cutoff = now - datetime.timedelta(days=DAYS_TO_KEEP)

# Iterate through log files and delete old ones
for filename in os.listdir(LOG_DIRECTORY):
    filepath = os.path.join(LOG_DIRECTORY, filename)
    if os.path.isfile(filepath):
        file_modified = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
        if file_modified < cutoff:
            os.remove(filepath)
            print(f"Deleted old log file: {filename}")
