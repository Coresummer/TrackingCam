import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(3,GPIO.OUT)
pwm = GPIO.PWM(3,50)
pwm.start(0)

def setAngle(angle):
    duty = angle /18 + 2
    GPIO.output(3,True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(3,False)
    pwm.ChangeDutyCycle(0)


setAngle(0)
pwm.stop()
GPIO.cleanup()
