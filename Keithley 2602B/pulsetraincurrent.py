import serial
import time
try: 
    ser1=serial.Serial('/dev/ttyACM0', 9600, timeout=10, parity = serial.PARITY_NONE) #Arduino serial port
except:
    print("No serial port for arduino")
for ii in range(100):
    quadState = "A0B0C0D0"
    ser1.write(quadState.encode())
    time.sleep(2)
    quadState = "A1B0C0D0"
    ser1.write(quadState.encode())
    time.sleep(2)
