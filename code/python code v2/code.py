import machine
import utime
import ustruct
import sys

# Micropython/raspi pico  example code
#
# Merged together these sources to make Adafruit code work with Micropython:
#
# https://www.digikey.com/en/maker/projects/raspberry-pi-pico-rp2040-i2c-example-with-micropython-and-cc/47d0c922b79342779cdbd4b37b7eb7e2
# https://github.com/adafruit/Adafruit_Python_BNO055/blob/ce9d7ae76cb23b8962d2dddc48f943bd8416831d/Adafruit_BNO055/BNO055.py
# https://github.com/adafruit/Adafruit_Python_BNO055/blob/ce9d7ae76cb23b8962d2dddc48f943bd8416831d/examples/simpletest.py
#
# - Used wiring diagram from digikey example - note, their unit swaps sda/scl
# - Eliminated RST pin - seems unnecessary
# - re-mapped code to use low-level read/write methods from digikey example
# - put everything into one file
# - de-classified the Adafruit object back into methods

###############################################################################
# Constants

# I2C addresses
BNO055_ADDRESS_A                     = 0x28
BNO055_ADDRESS_B                     = 0x29
BNO055_ID                            = 0xA0

# Page id register definition
BNO055_PAGE_ID_ADDR                  = 0X07

# PAGE0 REGISTER DEFINITION START
BNO055_CHIP_ID_ADDR                  = 0x00
BNO055_ACCEL_REV_ID_ADDR             = 0x01
BNO055_MAG_REV_ID_ADDR               = 0x02
BNO055_GYRO_REV_ID_ADDR              = 0x03
BNO055_SW_REV_ID_LSB_ADDR            = 0x04
BNO055_SW_REV_ID_MSB_ADDR            = 0x05
BNO055_BL_REV_ID_ADDR                = 0X06

# Accel data register
BNO055_ACCEL_DATA_X_LSB_ADDR         = 0X08
BNO055_ACCEL_DATA_X_MSB_ADDR         = 0X09
BNO055_ACCEL_DATA_Y_LSB_ADDR         = 0X0A
BNO055_ACCEL_DATA_Y_MSB_ADDR         = 0X0B
BNO055_ACCEL_DATA_Z_LSB_ADDR         = 0X0C
BNO055_ACCEL_DATA_Z_MSB_ADDR         = 0X0D

# Mag data register
BNO055_MAG_DATA_X_LSB_ADDR           = 0X0E
BNO055_MAG_DATA_X_MSB_ADDR           = 0X0F
BNO055_MAG_DATA_Y_LSB_ADDR           = 0X10
BNO055_MAG_DATA_Y_MSB_ADDR           = 0X11
BNO055_MAG_DATA_Z_LSB_ADDR           = 0X12
BNO055_MAG_DATA_Z_MSB_ADDR           = 0X13

# Gyro data registers
BNO055_GYRO_DATA_X_LSB_ADDR          = 0X14
BNO055_GYRO_DATA_X_MSB_ADDR          = 0X15
BNO055_GYRO_DATA_Y_LSB_ADDR          = 0X16
BNO055_GYRO_DATA_Y_MSB_ADDR          = 0X17
BNO055_GYRO_DATA_Z_LSB_ADDR          = 0X18
BNO055_GYRO_DATA_Z_MSB_ADDR          = 0X19

# Euler data registers
BNO055_EULER_H_LSB_ADDR              = 0X1A
BNO055_EULER_H_MSB_ADDR              = 0X1B
BNO055_EULER_R_LSB_ADDR              = 0X1C
BNO055_EULER_R_MSB_ADDR              = 0X1D
BNO055_EULER_P_LSB_ADDR              = 0X1E
BNO055_EULER_P_MSB_ADDR              = 0X1F

# Quaternion data registers
BNO055_QUATERNION_DATA_W_LSB_ADDR    = 0X20
BNO055_QUATERNION_DATA_W_MSB_ADDR    = 0X21
BNO055_QUATERNION_DATA_X_LSB_ADDR    = 0X22
BNO055_QUATERNION_DATA_X_MSB_ADDR    = 0X23
BNO055_QUATERNION_DATA_Y_LSB_ADDR    = 0X24
BNO055_QUATERNION_DATA_Y_MSB_ADDR    = 0X25
BNO055_QUATERNION_DATA_Z_LSB_ADDR    = 0X26
BNO055_QUATERNION_DATA_Z_MSB_ADDR    = 0X27

# Linear acceleration data registers
BNO055_LINEAR_ACCEL_DATA_X_LSB_ADDR  = 0X28
BNO055_LINEAR_ACCEL_DATA_X_MSB_ADDR  = 0X29
BNO055_LINEAR_ACCEL_DATA_Y_LSB_ADDR  = 0X2A
BNO055_LINEAR_ACCEL_DATA_Y_MSB_ADDR  = 0X2B
BNO055_LINEAR_ACCEL_DATA_Z_LSB_ADDR  = 0X2C
BNO055_LINEAR_ACCEL_DATA_Z_MSB_ADDR  = 0X2D

# Gravity data registers
BNO055_GRAVITY_DATA_X_LSB_ADDR       = 0X2E
BNO055_GRAVITY_DATA_X_MSB_ADDR       = 0X2F
BNO055_GRAVITY_DATA_Y_LSB_ADDR       = 0X30
BNO055_GRAVITY_DATA_Y_MSB_ADDR       = 0X31
BNO055_GRAVITY_DATA_Z_LSB_ADDR       = 0X32
BNO055_GRAVITY_DATA_Z_MSB_ADDR       = 0X33

# Temperature data register
BNO055_TEMP_ADDR                     = 0X34

# Status registers
BNO055_CALIB_STAT_ADDR               = 0X35
BNO055_SELFTEST_RESULT_ADDR          = 0X36
BNO055_INTR_STAT_ADDR                = 0X37

BNO055_SYS_CLK_STAT_ADDR             = 0X38
BNO055_SYS_STAT_ADDR                 = 0X39
BNO055_SYS_ERR_ADDR                  = 0X3A

# Unit selection register
BNO055_UNIT_SEL_ADDR                 = 0X3B
BNO055_DATA_SELECT_ADDR              = 0X3C

# Mode registers
BNO055_OPR_MODE_ADDR                 = 0X3D
BNO055_PWR_MODE_ADDR                 = 0X3E

BNO055_SYS_TRIGGER_ADDR              = 0X3F
BNO055_TEMP_SOURCE_ADDR              = 0X40

# Axis remap registers
BNO055_AXIS_MAP_CONFIG_ADDR          = 0X41
BNO055_AXIS_MAP_SIGN_ADDR            = 0X42

# Axis remap values
AXIS_REMAP_X                         = 0x00
AXIS_REMAP_Y                         = 0x01
AXIS_REMAP_Z                         = 0x02
AXIS_REMAP_POSITIVE                  = 0x00
AXIS_REMAP_NEGATIVE                  = 0x01

# SIC registers
BNO055_SIC_MATRIX_0_LSB_ADDR         = 0X43
BNO055_SIC_MATRIX_0_MSB_ADDR         = 0X44
BNO055_SIC_MATRIX_1_LSB_ADDR         = 0X45
BNO055_SIC_MATRIX_1_MSB_ADDR         = 0X46
BNO055_SIC_MATRIX_2_LSB_ADDR         = 0X47
BNO055_SIC_MATRIX_2_MSB_ADDR         = 0X48
BNO055_SIC_MATRIX_3_LSB_ADDR         = 0X49
BNO055_SIC_MATRIX_3_MSB_ADDR         = 0X4A
BNO055_SIC_MATRIX_4_LSB_ADDR         = 0X4B
BNO055_SIC_MATRIX_4_MSB_ADDR         = 0X4C
BNO055_SIC_MATRIX_5_LSB_ADDR         = 0X4D
BNO055_SIC_MATRIX_5_MSB_ADDR         = 0X4E
BNO055_SIC_MATRIX_6_LSB_ADDR         = 0X4F
BNO055_SIC_MATRIX_6_MSB_ADDR         = 0X50
BNO055_SIC_MATRIX_7_LSB_ADDR         = 0X51
BNO055_SIC_MATRIX_7_MSB_ADDR         = 0X52
BNO055_SIC_MATRIX_8_LSB_ADDR         = 0X53
BNO055_SIC_MATRIX_8_MSB_ADDR         = 0X54

# Accelerometer Offset registers
ACCEL_OFFSET_X_LSB_ADDR              = 0X55
ACCEL_OFFSET_X_MSB_ADDR              = 0X56
ACCEL_OFFSET_Y_LSB_ADDR              = 0X57
ACCEL_OFFSET_Y_MSB_ADDR              = 0X58
ACCEL_OFFSET_Z_LSB_ADDR              = 0X59
ACCEL_OFFSET_Z_MSB_ADDR              = 0X5A

# Magnetometer Offset registers
MAG_OFFSET_X_LSB_ADDR                = 0X5B
MAG_OFFSET_X_MSB_ADDR                = 0X5C
MAG_OFFSET_Y_LSB_ADDR                = 0X5D
MAG_OFFSET_Y_MSB_ADDR                = 0X5E
MAG_OFFSET_Z_LSB_ADDR                = 0X5F
MAG_OFFSET_Z_MSB_ADDR                = 0X60

# Gyroscope Offset register s
GYRO_OFFSET_X_LSB_ADDR               = 0X61
GYRO_OFFSET_X_MSB_ADDR               = 0X62
GYRO_OFFSET_Y_LSB_ADDR               = 0X63
GYRO_OFFSET_Y_MSB_ADDR               = 0X64
GYRO_OFFSET_Z_LSB_ADDR               = 0X65
GYRO_OFFSET_Z_MSB_ADDR               = 0X66

# Radius registers
ACCEL_RADIUS_LSB_ADDR                = 0X67
ACCEL_RADIUS_MSB_ADDR                = 0X68
MAG_RADIUS_LSB_ADDR                  = 0X69
MAG_RADIUS_MSB_ADDR                  = 0X6A

# Power modes
POWER_MODE_NORMAL                    = 0X00
POWER_MODE_LOWPOWER                  = 0X01
POWER_MODE_SUSPEND                   = 0X02

# Operation mode settings
OPERATION_MODE_CONFIG                = 0X00
OPERATION_MODE_ACCONLY               = 0X01
OPERATION_MODE_MAGONLY               = 0X02
OPERATION_MODE_GYRONLY               = 0X03
OPERATION_MODE_ACCMAG                = 0X04
OPERATION_MODE_ACCGYRO               = 0X05
OPERATION_MODE_MAGGYRO               = 0X06
OPERATION_MODE_AMG                   = 0X07
OPERATION_MODE_IMUPLUS               = 0X08
OPERATION_MODE_COMPASS               = 0X09
OPERATION_MODE_M4G                   = 0X0A
OPERATION_MODE_NDOF_FMC_OFF          = 0X0B
OPERATION_MODE_NDOF                  = 0X0C

###############################################################################

# global variables
addr=BNO055_ADDRESS_B

# Initialize I2C with pins
i2c = machine.I2C(0,
                  scl=machine.Pin(17),
                  sda=machine.Pin(16),
                  freq=100000)

###############################################################################
# Functions

def reg_write(reg, data):
    """
    Write bytes to the specified register.
    """
    global i2c

    # Construct message
    msg = bytearray()
    msg.append(data)
    
    # Write out message to register
    i2c.writeto_mem(addr, reg, msg)
    
def reg_read(reg, nbytes=1):
    """
    Read byte(s) from specified register. If nbytes > 1, read from consecutive
    registers.
    """
    global i2c
    
    # Check to make sure caller is asking for 1 or more bytes
    if nbytes < 1:
        return bytearray()
    
    # Request data from specified register(s) over I2C
    data = i2c.readfrom_mem(addr, reg, nbytes)
    return data




def _write_bytes(address, data, ack=True):
    # Write a list of 8-bit values starting at the provided register address.
    print("_write_bytes" + str(address) + "," + str(data))
    reg_write(address, data)

def _write_byte(address, value, ack=True):
    # Write an 8-bit value to the provided register address.  If ack is True
    # then expect an acknowledgement in serial mode, otherwise ignore any
    # acknowledgement (necessary when resetting the device).
    reg_write(address, value)

def _read_bytes(address, length):
    # Read a number of unsigned byte values starting from the provided address.
    return reg_read(address, length)

def _read_byte(address):
    # Read an 8-bit unsigned value from the provided register address.
    return reg_read(address)[0]

def _read_signed_byte(address):
    # Read an 8-bit signed value from the provided register address.
    data = _read_byte(address)
    if data > 127:
        return data - 256
    else:
        return data

def _config_mode():
    # Enter configuration mode.
    set_mode(OPERATION_MODE_CONFIG)

def _operation_mode():
    # Enter operation mode to read sensor data.
    set_mode(OPERATION_MODE_NDOF)

def begin():
    """Initialize the BNO055 sensor.  Must be called once before any other
    BNO055 library functions.  Will return True if the BNO055 was
    successfully initialized, and False otherwise.
    """
    # First send a thow-away command and ignore any response or I2C errors
    # just to make sure the BNO is in a good state and ready to accept
    # commands (this seems to be necessary after a hard power down).  
    try:
        _write_byte(BNO055_PAGE_ID_ADDR, 0, ack=False)
    except Exception:
        # Swallow an IOError that might be raised by an I2C issue.  Only do
        # this for this very first command to help get the BNO and board's
        # I2C into a clear state ready to accept the next commands.
        print("there was an exception writing a byte")
        pass
    # Make sure we're in config mode and on page 0.
    _config_mode()   
    _write_byte(BNO055_PAGE_ID_ADDR, 0)
    # Check the chip ID
    bno_id = _read_byte(BNO055_CHIP_ID_ADDR)
    #logger.debug('Read chip ID: 0x{0:02X}'.format(bno_id))
    if bno_id != BNO055_ID:
        print("bno_id=" +str(bno_id) + ","+str(BNO055_ID))
        return False
    # Reset the device.
    _write_byte(BNO055_SYS_TRIGGER_ADDR, 0x20, ack=False)
    # Wait 650ms after reset for chip to be ready (as suggested
    # in datasheet).
    utime.sleep(0.65)
    # Set to normal power mode.
    _write_byte(BNO055_PWR_MODE_ADDR, POWER_MODE_NORMAL)
    # Default to internal oscillator.
    _write_byte(BNO055_SYS_TRIGGER_ADDR, 0x0)
    # Enter normal operation mode.
    _operation_mode()
    return True

def set_mode(mode):
    """Set operation mode for BNO055 sensor.  Mode should be a value from
    table 3-3 and 3-5 of the datasheet:
      http://www.adafruit.com/datasheets/BST_BNO055_DS000_12.pdf
    """
    _write_byte(BNO055_OPR_MODE_ADDR, mode & 0xFF)
    # Delay for 30 milliseconds (datsheet recommends 19ms, but a little more
    # can't hurt and the kernel is going to spend some unknown amount of time
    # too).
    utime.sleep(0.03)

def get_revision():
    """Return a tuple with revision information about the BNO055 chip.  Will
    return 5 values:
      - Software revision
      - Bootloader version
      - Accelerometer ID
      - Magnetometer ID
      - Gyro ID
    """
    # Read revision values.
    accel = _read_byte(BNO055_ACCEL_REV_ID_ADDR)
    mag = _read_byte(BNO055_MAG_REV_ID_ADDR)
    gyro = _read_byte(BNO055_GYRO_REV_ID_ADDR)
    bl = _read_byte(BNO055_BL_REV_ID_ADDR)
    sw_lsb = _read_byte(BNO055_SW_REV_ID_LSB_ADDR)
    sw_msb = _read_byte(BNO055_SW_REV_ID_MSB_ADDR)
    sw = ((sw_msb << 8) | sw_lsb) & 0xFFFF
    # Return the results as a tuple of all 5 values.
    return (sw, bl, accel, mag, gyro)

def set_external_crystal(external_crystal):
    """Set if an external crystal is being used by passing True, otherwise
    use the internal oscillator by passing False (the default behavior).
    """
    # Switch to configuration mode.
    _config_mode()
    # Set the clock bit appropriately in the SYS_TRIGGER register.
    if external_crystal:
        _write_byte(BNO055_SYS_TRIGGER_ADDR, 0x80)
    else:
        _write_byte(BNO055_SYS_TRIGGER_ADDR, 0x00)
    # Go back to normal operation mode.
    _operation_mode()

def get_system_status(run_self_test=True):
    """Return a tuple with status information.  Three values will be returned:
      - System status register value with the following meaning:
          0 = Idle
          1 = System Error
          2 = Initializing Peripherals
          3 = System Initialization
          4 = Executing Self-Test
          5 = Sensor fusion algorithm running
          6 = System running without fusion algorithms
      - Self test result register value with the following meaning:
          Bit value: 1 = test passed, 0 = test failed
          Bit 0 = Accelerometer self test
          Bit 1 = Magnetometer self test
          Bit 2 = Gyroscope self test
          Bit 3 = MCU self test
          Value of 0x0F = all good!
      - System error register value with the following meaning:
          0 = No error
          1 = Peripheral initialization error
          2 = System initialization error
          3 = Self test result failed
          4 = Register map value out of range
          5 = Register map address out of range
          6 = Register map write error
          7 = BNO low power mode not available for selected operation mode
          8 = Accelerometer power mode not available
          9 = Fusion algorithm configuration error
         10 = Sensor configuration error
    If run_self_test is passed in as False then no self test is performed and
    None will be returned for the self test result.  Note that running a
    self test requires going into config mode which will stop the fusion
    engine from running.
    """
    self_test = None
    if run_self_test:
        # Switch to configuration mode if running self test.
        _config_mode()
        # Perform a self test.
        sys_trigger = _read_byte(BNO055_SYS_TRIGGER_ADDR)
        _write_byte(BNO055_SYS_TRIGGER_ADDR, sys_trigger | 0x1)
        # Wait for self test to finish.
        utime.sleep(1.0)
        # Read test result.
        self_test = _read_byte(BNO055_SELFTEST_RESULT_ADDR)
        # Go back to operation mode.
        _operation_mode()
    # Now read status and error registers.
    status = _read_byte(BNO055_SYS_STAT_ADDR)
    error = _read_byte(BNO055_SYS_ERR_ADDR)
    # Return the results as a tuple of all 3 values.
    return (status, self_test, error)

def get_calibration_status():
    """Read the calibration status of the sensors and return a 4 tuple with
    calibration status as follows:
      - System, 3=fully calibrated, 0=not calibrated
      - Gyroscope, 3=fully calibrated, 0=not calibrated
      - Accelerometer, 3=fully calibrated, 0=not calibrated
      - Magnetometer, 3=fully calibrated, 0=not calibrated
    """
    # Return the calibration status register value.
    cal_status = _read_byte(BNO055_CALIB_STAT_ADDR)
    sys = (cal_status >> 6) & 0x03
    gyro = (cal_status >> 4) & 0x03
    accel = (cal_status >> 2) & 0x03
    mag = cal_status & 0x03
    # Return the results as a tuple of all 3 values.
    return (sys, gyro, accel, mag)

def get_calibration():
    """Return the sensor's calibration data and return it as an array of
    22 bytes. Can be saved and then reloaded with the set_calibration function
    to quickly calibrate from a previously calculated set of calibration data.
    """
    # Switch to configuration mode, as mentioned in section 3.10.4 of datasheet.
    _config_mode()
    # Read the 22 bytes of calibration data and convert it to a list (from
    # a bytearray) so it's more easily serialized should the caller want to
    # store it.
    cal_data = list(_read_bytes(ACCEL_OFFSET_X_LSB_ADDR, 22))
    # Go back to normal operation mode.
    _operation_mode()
    return cal_data

def set_calibration(data):
    """Set the sensor's calibration data using a list of 22 bytes that
    represent the sensor offsets and calibration data.  This data should be
    a value that was previously retrieved with get_calibration (and then
    perhaps persisted to disk or other location until needed again).
    """
    # Check that 22 bytes were passed in with calibration data.
    if data is None or len(data) != 22:
        raise ValueError('Expected a list of 22 bytes for calibration data.')
    # Switch to configuration mode, as mentioned in section 3.10.4 of datasheet.
    _config_mode()
    # Set the 22 bytes of calibration data.
    _write_bytes(ACCEL_OFFSET_X_LSB_ADDR, data)
    # Go back to normal operation mode.
    _operation_mode()

def get_axis_remap():
    """Return a tuple with the axis remap register values.  This will return
    6 values with the following meaning:
      - X axis remap (a value of AXIS_REMAP_X, AXIS_REMAP_Y, or AXIS_REMAP_Z.
                      which indicates that the physical X axis of the chip
                      is remapped to a different axis)
      - Y axis remap (see above)
      - Z axis remap (see above)
      - X axis sign (a value of AXIS_REMAP_POSITIVE or AXIS_REMAP_NEGATIVE
                     which indicates if the X axis values should be positive/
                     normal or negative/inverted.  The default is positive.)
      - Y axis sign (see above)
      - Z axis sign (see above)
    Note that by default the axis orientation of the BNO chip looks like
    the following (taken from section 3.4, page 24 of the datasheet).  Notice
    the dot in the corner that corresponds to the dot on the BNO chip:
                       | Z axis
                       |
                       |   / X axis
                   ____|__/____
      Y axis     / *   | /    /|
      _________ /______|/    //
               /___________ //
              |____________|/
    """
    # Get the axis remap register value.
    map_config = _read_byte(BNO055_AXIS_MAP_CONFIG_ADDR)
    z = (map_config >> 4) & 0x03
    y = (map_config >> 2) & 0x03
    x = map_config & 0x03
    # Get the axis remap sign register value.
    sign_config = _read_byte(BNO055_AXIS_MAP_SIGN_ADDR)
    x_sign = (sign_config >> 2) & 0x01
    y_sign = (sign_config >> 1) & 0x01
    z_sign = sign_config & 0x01
    # Return the results as a tuple of all 3 values.
    return (x, y, z, x_sign, y_sign, z_sign)

def set_axis_remap(x, y, z,
                   x_sign=AXIS_REMAP_POSITIVE, y_sign=AXIS_REMAP_POSITIVE,
                   z_sign=AXIS_REMAP_POSITIVE):
    """Set axis remap for each axis.  The x, y, z parameter values should
    be set to one of AXIS_REMAP_X, AXIS_REMAP_Y, or AXIS_REMAP_Z and will
    change the BNO's axis to represent another axis.  Note that two axises
    cannot be mapped to the same axis, so the x, y, z params should be a
    unique combination of AXIS_REMAP_X, AXIS_REMAP_Y, AXIS_REMAP_Z values.
    The x_sign, y_sign, z_sign values represent if the axis should be positive
    or negative (inverted).
    See the get_axis_remap documentation for information on the orientation
    of the axises on the chip, and consult section 3.4 of the datasheet.
    """
    # Switch to configuration mode.
    _config_mode()
    # Set the axis remap register value.
    map_config = 0x00
    map_config |= (z & 0x03) << 4
    map_config |= (y & 0x03) << 2
    map_config |= x & 0x03
    _write_byte(BNO055_AXIS_MAP_CONFIG_ADDR, map_config)
    # Set the axis remap sign register value.
    sign_config = 0x00
    sign_config |= (x_sign & 0x01) << 2
    sign_config |= (y_sign & 0x01) << 1
    sign_config |= z_sign & 0x01
    _write_byte(BNO055_AXIS_MAP_SIGN_ADDR, sign_config)
    # Go back to normal operation mode.
    _operation_mode()

def _read_vector(address, count=3):
    # Read count number of 16-bit signed values starting from the provided
    # address. Returns a tuple of the values that were read.
    data = _read_bytes(address, count*2)
    result = [0]*count
    for i in range(count):
        result[i] = ((data[i*2+1] << 8) | data[i*2]) & 0xFFFF
        if result[i] > 32767:
            result[i] -= 65536
    return result

def read_euler():
    """Return the current absolute orientation as a tuple of heading, roll,
    and pitch euler angles in degrees.
    """
    heading, roll, pitch = _read_vector(BNO055_EULER_H_LSB_ADDR)
    return (heading/16.0, roll/16.0, pitch/16.0)

def read_magnetometer():
    """Return the current magnetometer reading as a tuple of X, Y, Z values
    in micro-Teslas.
    """
    x, y, z = _read_vector(BNO055_MAG_DATA_X_LSB_ADDR)
    return (x/16.0, y/16.0, z/16.0)

def read_gyroscope():
    """Return the current gyroscope (angular velocity) reading as a tuple of
    X, Y, Z values in degrees per second.
    """
    x, y, z = _read_vector(BNO055_GYRO_DATA_X_LSB_ADDR)
    return (x/900.0, y/900.0, z/900.0)

def read_accelerometer():
    """Return the current accelerometer reading as a tuple of X, Y, Z values
    in meters/second^2.
    """
    x, y, z = _read_vector(BNO055_ACCEL_DATA_X_LSB_ADDR)
    return (x/100.0, y/100.0, z/100.0)

def read_linear_acceleration():
    """Return the current linear acceleration (acceleration from movement,
    not from gravity) reading as a tuple of X, Y, Z values in meters/second^2.
    """
    x, y, z = _read_vector(BNO055_LINEAR_ACCEL_DATA_X_LSB_ADDR)
    return (x/100.0, y/100.0, z/100.0)

def read_gravity():
    """Return the current gravity acceleration reading as a tuple of X, Y, Z
    values in meters/second^2.
    """
    x, y, z = _read_vector(BNO055_GRAVITY_DATA_X_LSB_ADDR)
    return (x/100.0, y/100.0, z/100.0)

def read_quaternion():
    """Return the current orientation as a tuple of X, Y, Z, W quaternion
    values.
    """
    w, x, y, z = _read_vector(BNO055_QUATERNION_DATA_W_LSB_ADDR, 4)
    # Scale values, see 3.6.5.5 in the datasheet.
    scale = (1.0 / (1<<14))
    return (x*scale, y*scale, z*scale, w*scale)

def read_temp():
    """Return the current temperature in Celsius."""
    return _read_signed_byte(BNO055_TEMP_ADDR)

###############################################################################


# Settings



###############################################################################
# Main

# Initialize the BNO055 and stop if something went wrong.
if not begin():
    raise RuntimeError('Failed to initialize BNO055! Is the sensor connected?')
# 
# Print system status and self test result.
status, self_test, error = get_system_status()
print('System status: {0}'.format(status))
print('Self test result (0x0F is normal): 0x{0:02X}'.format(self_test))
# Print out an error if system status is in error mode.
if status == 0x01:
    print('System error: {0}'.format(error))
    print('See datasheet section 4.3.59 for the meaning.')
 
# Print BNO055 software revision and other diagnostic data.
sw, bl, accel, mag, gyro = get_revision()
print('Software version:   {0}'.format(sw))
print('Bootloader version: {0}'.format(bl))
print('Accelerometer ID:   0x{0:02X}'.format(accel))
print('Magnetometer ID:    0x{0:02X}'.format(mag))
print('Gyroscope ID:       0x{0:02X}\n'.format(gyro))

print('Reading BNO055 data, press Ctrl-C to quit...')
while True:
    # Read the Euler angles for heading, roll, pitch (all in degrees).
    heading, roll, pitch = read_euler()
    # Read the calibration status, 0=uncalibrated and 3=fully calibrated.
    sys, gyro, accel, mag = get_calibration_status()
    # Print everything out.
    print('Heading={0:0.2F} Roll={1:0.2F} Pitch={2:0.2F}\tSys_cal={3} Gyro_cal={4} Accel_cal={5} Mag_cal={6}'.format(
          heading, roll, pitch, sys, gyro, accel, mag))
    # Other values you can optionally read:
    # Orientation as a quaternion:
    #x,y,z,w = read_quaterion()
    # Sensor temperature in degrees Celsius:
    temp_c = read_temp()
    print("Temp: " + str((temp_c * 1.8) + 32.0))
    # Magnetometer data (in micro-Teslas):
    #x,y,z = read_magnetometer()
    # Gyroscope data (in degrees per second):
    #x,y,z = read_gyroscope()
    # Accelerometer data (in meters per second squared):
    #x,y,z = read_accelerometer()
    # Linear acceleration data (i.e. acceleration from movement, not gravity--
    # returned in meters per second squared):
    #x,y,z = read_linear_acceleration()
    # Gravity acceleration data (i.e. acceleration just from gravity--returned
    # in meters per second squared):
    #x,y,z = read_gravity()
    # Sleep for a second until the next reading.
    utime.sleep(1)