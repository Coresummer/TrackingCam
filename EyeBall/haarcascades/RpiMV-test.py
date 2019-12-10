import time
import numpy as np
import threading
import RPi.GPIO as GPIO
import wiringpi as wp

#GPIO.setmode(GPIO.BCM)
gp_outX = 8
gp_outY = 9

DUTY_MAX = 123
DUTY_MIN = 26
DUTY_HOME = 74
duty = 0

fan = 24
fan2 = 26
respTime = 0.01
AcSpeed = 3
standard = 7.5
s_hold = 50
FPS = 30

wp.wiringPiSetupGpio()
wp.pinMode(gp_outX, wp.GPIO.PWM_OUTPUT)
wp.pwmSetMode(wp.GPIO.PWM_MODE_MS)
wp.pwmSetClock(375)

wp.pwmWrite(gp_outX,DUTY_HOME)
wp.delay(100)

def move(degree):
    duty = int((DUTY_MAX-DUTY_MIN)/180.0 * degree + DUTY_HOME)
    wp.pwmWrite(gp_outX,duty)

#GPIO.setup(fan,GPIO.OUT)
#GPIO.output(fan,1)

for degree in [0,45,90,0,-45,-90,0,30,-30,0]:
    move(degree)
    wp.delay(500)
