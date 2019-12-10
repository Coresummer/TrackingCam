import serial
import time
import re
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
gp_outX = 3
gp_outY = 2
standard = 52
respTime = 0.005
AcRange = 2

GPIO.setup(gp_outX, GPIO.OUT)
GPIO.setup(gp_outY, GPIO.OUT)

servoX = GPIO.PWM(gp_outX, 50)
servoY = GPIO.PWM(gp_outY, 50)
servoX.start(50)
servoY.start(50)
def main():
    data = [0,0]
    con = serial.Serial('/dev/ttyACM0',9600)
    time.sleep(2)
    print con.portstr
    while 1:
        for i in range(2):
            stre = con.read_until('k')
            value = re.sub(r'\D','', stre)
            data[i] = int(value)
        print data
        if(data[0] - standard != 0 or data[1] - standard != 0):
            if(data[0] - standard > 0): servoX.ChangeDutyCycle(7.5 + (data[0] - standard)*1.3)
            elif(data[0] - standard < 0): servoX.ChangeDutyCycle(7.5 - (standard - data[0])*1.3)
            else: servoX.ChangeDutyCycle(0)

            if(data[1] - standard > 0): servoY.ChangeDutyCycle(7.5 + (data[1] - standard)*1.3)
            elif(data[1] - standard < 0): servoY.ChangeDutyCycle(7.5 - (standard - data[1])*1.3)
            else: servoY.ChangeDutyCycle(0)  
            time.sleep(respTime)
            servoX.start(50)
            servoY.start(50)
if __name__ == '__main__':
        main()
