# code/logger.py
import os
import time

def create_log_file():
    """
    Creates a new log file with a unique timestamped name and writes the header.
    """
    # Ensure the /logs directory exists.
    try:
        os.stat("/logs")
    except OSError:
        os.mkdir("/logs")
    
    lt = time.localtime()[:6]
    timestamp = "{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d}".format(*lt)
    log_filename = "/logs/cycle_log_{}.csv".format(timestamp)
    
    with open(log_filename, "w") as f:
        f.write("Timestamp,Cycle,Temperature,Heater Name,Heater Power,Fan Power\n")
    return log_filename

def log_cycle_data(log_filename, cycle, temperature, heater_name, heater_power, fan_power):
    """
    Logs a single CSV-formatted line to the log file.
    """
    lt = time.localtime()[:6]
    timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*lt)
    log_entry = "{},{},{:.2f},{},{:.2f},{:.2f}\n".format(timestamp, cycle, temperature, heater_name, heater_power, fan_power)
    
    with open(log_filename, "a") as f:
        f.write(log_entry)
    print("Logged:", log_entry.strip())