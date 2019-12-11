import cv2
import time
import numpy as np
import threading
from multiprocessing import Process
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
gp_outX = 3
gp_outY = 2
fan = 24
respTime = 0.1
AcSpeed = 3
standard = 7.5
s_hold = 50
FPS = 3

ANGLE_MAX = 120
ANGLE_HOME = 60
ANGLE_MIN = 0

GPIO.setup(gp_outX,GPIO.OUT)
servoX = GPIO.PWM(gp_outX, s_hold)
servoX.start(0)

GPIO.setup(gp_outY,GPIO.OUT)
servoY = GPIO.PWM(gp_outY, s_hold)
servoY.start(0)

GPIO.setup(fan,GPIO.OUT)
GPIO.output(fan,1)

Current_AngleX = 60
Current_AngleY = 60
new_angleX = 60
new_angleY = 60

def DrawFrame(_frame, _name):
    cv2.imshow(_name,_frame)
    cv2.waitKey() & 0.12

def SetAngle(angleX,angleY,c_angleX,c_angleY):
    if angleX != c_angleX or angleY != c_angleY:

        dutyX = angleX/24 + 5
        dutyY = angleY/24 + 5
        print("DutyX")
        print(dutyX)
        print("DutyY")
        print(dutyY)
        servoX.ChangeDutyCycle(dutyX)
        servoY.ChangeDutyCycle(dutyY)
        time.sleep(respTime)
        servoX.ChangeDutyCycle(0)
        servoY.ChangeDutyCycle(0)
    else:
        servoX.ChangeDutyCycle(0)
        servoY.ChangeDutyCycle(0)

if __name__ == '__main__':
    threshold = 80
    
    URL = "http://localhost:8080/?action=stream"

    #Set color for face detection
    rectangle_color = (0, 0, 255) #緑色
    #Prepare Video stream
    video = cv2.VideoCapture(0)
    video.set(7,FPS)
    videoW = video.get(3)
    videoH = video.get(4)

    print(videoW)
    print(videoH)

    centerX = videoW/2
    centerY = videoH/2

    #Prepare cascade classifier by trained model
    cascade_path = 'haarcascade_frontalface_default.xml'
    cascade = cv2.CascadeClassifier(cascade_path)

    #Flag for tracker
    initBB = None
    #set up tracler By KCF algorithm

while video.isOpened():
    #read video frame
    for i in range(FPS): ret, frame = video.read()
    #ret, frame = video.read()
    
    #if video frame dosent exist, break
    if not ret: break
    #when tracking is not on
    if initBB is None:
        facerect = cascade.detectMultiScale(frame, scaleFactor=1.3, minNeighbors=1, minSize=(80, 80))
        # when face detected
        if len(facerect) > 0:
            initBB = (facerect[0][0]/2,facerect[0][1]/2,facerect[0][0]+facerect[0][2],facerect[0][1]+facerect[0][3])
            print("Detected!:")
            print(initBB)
            tracker = cv2.TrackerMedianFlow_create() #MedianFlow is also pretty good
            #tracker = cv2.TrackerTLD_create()
            tracker.init(frame, initBB)
            for rect in facerect:
                cv2.rectangle(frame,tuple(rect[0:2]), tuple(rect[0:2]+rect[2:4]),rectangle_color,thickness=2)
            
    #when tracking is on
    else:
        (success, box) = tracker.update(frame)
        # check to see if the tracking was a success
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h),(0, 255, 0), 2)
            #Calculate positon
            #cv2.circle(frame,(int(x+w/2),int(y+h/2)),4,(255,0,0),2)
            print("coordinate:")
            print((x,y,w,h))

            #move servo motor
            diffX = ((centerX - (x + w/2)) / videoW/2) * 150
            diffY = ((centerY - (y + h/2)) / videoH/2) * 150

            #if diffX > 0: new_angleX = Current_AngleX + 5
            #elif diffX < 0: new_angleX = Current_AngleX - 5
            #else: new_angleX = Current_AngleX

            #if diffY > 0: new_angleY = Current_AngleY + 5
            #elif diffY < 0: new_angleY = Current_AngleY - 5
            #else: new_angleY = Current_AngleY

            print(diffX)
            print(diffY)

            new_angleX = Current_AngleX + diffX
            new_angleY = Current_AngleY + diffY

            if(new_angleX > ANGLE_MAX): new_angleX = ANGLE_MAX
            elif(new_angleX < ANGLE_MIN): new_angleX = ANGLE_MIN
            if(new_angleY > ANGLE_MAX): new_angleY = ANGLE_MAX
            elif(new_angleY < ANGLE_MIN): new_angleY = ANGLE_MIN

            thread_s = threading.Thread(target=SetAngle, args=(new_angleX,new_angleY,Current_AngleX,Current_AngleY))
            thread_s.start()

            if(new_angleX != Current_AngleX or new_angleY != Current_AngleY):
                Current_AngleX = new_angleX
                Current_AngleY = new_angleY

        else:
            print("-------Lost Target--------")
            initBB = None
    #thread = threading.Thread(target=DrawFrame, args=(frame,'frame'))    
    #thread.start()
#メモリの解放
video.release()
cv2.destroyAllWindows()
