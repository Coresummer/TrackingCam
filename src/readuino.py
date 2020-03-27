#!/usr/bin/env python
# -*- coding: utf-8 -*-

import serial
import time
import re
import RPi.GPIO as GPIO
import cv2

GPIO.setmode(GPIO.BCM)
gp_outX = 3
gp_outY = 2
standard = 52
respTime = 0.01
AcSpeed = 0.1

URL = "http://localhost:8080/?action=stream"
s_video = cv2.VideoCapture(URL)

GPIO.setup(gp_outX, GPIO.OUT)
GPIO.setup(gp_outY, GPIO.OUT)

servoX = GPIO.PWM(gp_outX, 50)
servoY = GPIO.PWM(gp_outY, 50)

servoX.start(50)
servoY.start(50)

def main():
    data = [0,0]
    con = serial.Serial(port = '/dev/ttyACM0', baudrate =  9600, timeout = 0, rtscts = True)
    time.sleep(2)
    print(con.port)
    while 1:
        ret, img = s_video.read()
        cv2.imshow("Stream Video",img)

        for i in range(2):
            stre = con.read_until('k').decode('utf-8')
            value = re.sub('\D','', stre)
            print(value)
            data[i] = int(value)
        print(data)
        if(data[0] - standard != 0 or data[1] - standard != 0):
            if(data[0] - standard > 0): servoX.ChangeDutyCycle(7.5 + (data[0] - standard)*AcSpeed)
            elif(data[0] - standard < 0): servoX. ChangeDutyCycle(7.5 - (standard - data[0])*AcSpeed)

            if(data[1] - standard > 0): servoY.ChangeDutyCycle(7.5 + (data[1] - standard)*AcSpeed)
            elif(data[1] - standard < 0): servoY. ChangeDutyCycle(7.5 - (standard - data[1])*AcSpeed)
            time.sleep(respTime)
            servoX.ChangeDutyCycle(50)
            servoY.ChangeDutyCycle(50)


if __name__ == '__main__':
        main()