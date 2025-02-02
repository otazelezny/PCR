import os
import time

def create_log_file():
    """
    Creates a new log file with a unique timestamped name and writes the header row.
    """
    timestamp = "{:04d}{:02d}{:02d}-{:02d}{:02d}{:02d}".format(*time.localtime()[:6])
    log_filename = f"logs/cycle_log_{timestamp}.csv"

    # Check if 'logs' directory exists, create if not
    try:
        os.stat("logs")  # Check if directory exists
    except OSError:
        os.mkdir("logs")  # Create it if it doesn't exist

    with open(log_filename, "w") as file:
        file.write("Timestamp,Cycle,Temperature,Heater Name,Heater Power,Fan Power\n")

    return log_filename

def log_cycle_data(log_filename, cycle, temperature, heater_name, heater_power, fan_power):
    """
    Logs temperature, heater power, and fan power into the specified log file.
    """
    timestamp = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*time.localtime()[:6])
    
    log_entry = f"{timestamp},{cycle},{temperature},{heater_name},{heater_power},{fan_power}\n"

    with open(log_filename, "a") as file:
        file.write(log_entry)

    print(f"Logged: {timestamp}, Cycle {cycle}, Temp: {temperature}°C, Heater {heater_name}: {heater_power:.2f}%, Fan: {fan_power:.2f}%")