import serial
import time


ser = serial.Serial('/dev/ttyACM0', baudrate=115200, dsrdtr=False)
ser.setDTR(False)

def mph2pw( mph ):
    if mph > 5.0:
        mph = 5.0;
    lpw = -0.0620747 * mph + 0.92;
    # linear regression is not perfect
    if mph <= 0.5:
        lpw = 1
    return lpw

seconds = 0.0
miles = 0.0
mph = 0.0
prev_mph = mph
start = time.time()
end = time.time()

while 1:
    end = time.time()
    duration = end-start
    miles = miles + prev_mph*duration/3600
    if prev_mph > 0.001:
        seconds = seconds + (end-start)
    start = end
    prev_mph = mph

    print str(seconds) + " seconds elapsed, " + str(miles) + " miles walked"
    mph = float(raw_input('Enter speed in MPH: '))
    pw = mph2pw(mph)
    print pw
    ser.write(str(pw))
    
