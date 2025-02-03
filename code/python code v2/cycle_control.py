# code/cycle_control.py
import time
from pid import PID
from logger import log_cycle_data
from heater import set_heater_power, stop_heater
from fan import set_fan_speed, stop_fan
from safety import check_safety
from sensors import read_temperatures

def run_cycles(config, sensors, heaters, fan, log_filename):
    """
    Runs the PCR cycles as defined in the configuration.
    """
    cycles_config = config["Cycles"]
    cycles_count = cycles_config.get("cycles_count", 1)
    # List the cycle phases in the desired order.
    phase_names = [ "start_denaturation", "denaturation", "annealing", "extension", "final_extension" ]
    
    for cycle_iter in range(1, cycles_count + 1):
        print("=== Starting cycle iteration: {} ===".format(cycle_iter))
        for phase in phase_names:
            if phase in cycles_config:
                phase_config = cycles_config[phase]
                print("=== Starting phase: {} ===".format(phase))
                run_phase(phase, phase_config, sensors, heaters, fan, log_filename, config["safety_limits"])
            else:
                print("Phase {} not defined in config.".format(phase))
    print("All cycles complete.")

def run_phase(phase_name, phase_config, sensors, heaters, fan, log_filename, safety_limits):
    """
    Runs one phase of the PCR cycle.
    """
    target_temp = phase_config["target_temp"]
    duration = phase_config["time"]
    # PID parameters for heating
    pid_kp = phase_config["pid_kp"]
    pid_ki = phase_config["pid_ki"]
    pid_kd = phase_config["pid_kd"]
    # PID parameters for cooling (fan)
    cooling_kp = phase_config.get("cooling_kp", 1.5)
    cooling_ki = phase_config.get("cooling_ki", 0.2)
    cooling_kd = phase_config.get("cooling_kd", 0.05)
    
    # Initialize a PID for each heater.
    for heater in heaters.values():
        heater["pid"] = PID(kp=pid_kp, ki=pid_ki, kd=pid_kd, setpoint=target_temp)
    # Create one PID controller for cooling.
    cooling_pid = PID(kp=cooling_kp, ki=cooling_ki, kd=cooling_kd, setpoint=target_temp)
    
    start_time = time.time()
    elapsed = 0
    while elapsed < duration:
        temp_readings = read_temperatures(sensors)
        # Safety check – if a sensor reading violates limits, the shutdown occurs.
        if not check_safety(temp_readings, safety_limits, heaters, fan):
            return  # Exit phase immediately
        
        # For simplicity, compute the average temperature from all sensors.
        if temp_readings:
            avg_temp = sum(temp_readings.values()) / len(temp_readings)
        else:
            avg_temp = 0
        print("Phase {}: Average Temperature: {:.2f}°C".format(phase_name, avg_temp))
        
        if avg_temp < target_temp:
            # Heating mode: update each heater using its PID.
            for heater in heaters.values():
                output = heater["pid"].compute(avg_temp)
                power = max(0, min(100, output))
                set_heater_power(heater, power)
                log_cycle_data(log_filename, phase_name, avg_temp, heater["name"], power, 0)
            # Turn off the fan.
            set_fan_speed(fan, 0)
        else:
            # Cooling mode: turn off heaters and use the cooling PID for the fan.
            for heater in heaters.values():
                set_heater_power(heater, 0)
                log_cycle_data(log_filename, phase_name, avg_temp, heater["name"], 0, 0)
            fan_output = cooling_pid.compute(avg_temp)
            # Ensure the fan runs at a minimum speed when cooling.
            fan_power = max(30, min(100, fan_output))
            set_fan_speed(fan, fan_power)
            # Log fan activity (for each heater, for consistency).
            for heater in heaters.values():
                log_cycle_data(log_filename, phase_name, avg_temp, heater["name"], 0, fan_power)
        
        time.sleep(1)
        elapsed = time.time() - start_time
    
    # End of phase: shut down heaters and fan.
    for heater in heaters.values():
        stop_heater(heater)
    stop_fan(fan)
    print("Phase {} complete.".format(phase_name))