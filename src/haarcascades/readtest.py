#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import serial
import time
import re
import RPi.GPIO as GPIO
import cv2

face_cascade_path = "haarcascade_frontalface_default.xml"
eye_cascade_path = "haarcascade_eye.xml"

face_cascade = cv2.CascadeClassifier(face_cascade_path)
eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

color = (255,0,0)

GPIO.setmode(GPIO.BCM)
gp_outX = 3
gp_outY = 2
fan = 24
fan2 = 26
standard = 52
respTime = 0.01
AcSpeed = 0.6

URL = "http://localhost:8080/?action=stream"
s_video = cv2.VideoCapture(URL)
s_video.set(cv2.CAP_PROP_BUFFERSIZE,30)
print(s_video.isOpened())

GPIO.setup(gp_outX, GPIO.OUT)
GPIO.setup(gp_outY, GPIO.OUT)
GPIO.setup(fan,GPIO.OUT)
GPIO.output(fan,1)
GPIO.setup(fan2,GPIO.OUT)
GPIO.output(fan2,1)
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
        for i in range(30): ret, img = s_video.read()
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        facerect = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30,30),
        )
        if len(facerect>0):
            for rect in facerect:
                cv2.rectangle(img, tuple(rect[0:2]),tuple(rect[0:2]+rect[2:4]),color,thickness=2)
        else:print("no face")
        cv2.imshow("detected.jpg",img)
        for i in range(2):
            stre = con.read(4).decode('utf-8')
            value = re.sub(r'\D','',stre)
            if(value != '' and int(value)<standard+5 and int(value)>standard-5 ): data[i] = int(value)
            else: data[i] = standard
            print(data)
        if(data[0] - standard != 0 or data[1] - standard != 0):
            if(data[0] - standard > 0): servoX.ChangeDutyCycle(7.5 + (data[0] - standard)*AcSpeed)
            elif(data[0] - standard < 0): servoX. ChangeDutyCycle(7.5 - (standard - data[0])*AcSpeed)
            if(data[1] - standard > 0): servoY.ChangeDutyCycle(7.5 + (data[1] - standard)*AcSpeed)
            elif(data[1] - standard < 0): servoY. ChangeDutyCycle(7.5 - (standard - data[1])*AcSpeed)
        time.sleep(0.01)
        servoX.ChangeDutyCycle(50)
        servoY.ChangeDutyCycle(50)
        cv2.waitKey(1) & 0xff
if __name__ == '__main__':
        main()
