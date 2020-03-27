import cv2
import time
import numpy as np
import threading
import RPi.GPIO as GPIO
from multiprocessing import Process

GPIO.setmode(GPIO.BCM)
gp_outX = 3
gp_outY = 2
fan = 24
fan2 = 26
respTime = 0.01
AcSpeed = 3
standard = 7.5
s_hold = 50
FPS = 30

GPIO.setup(gp_outX,GPIO.OUT)
servoX = GPIO.PWM(gp_outX, s_hold)
servoX.start(s_hold)

GPIO.setup(gp_outY,GPIO.OUT)
servoY = GPIO.PWM(gp_outY, s_hold)
servoY.start(s_hold)

GPIO.setup(fan,GPIO.OUT)
GPIO.output(fan,1)

def Left():
    print("Left")
    servoX.ChangeDutyCycle(standard+AcSpeed)
    time.sleep(respTime)
    servoX.ChangeDutyCycle(s_hold)
    #time.sleep(100*respTime)

def Right():
    print("Right")
    servoX.ChangeDutyCycle(standard-AcSpeed)
    time.sleep(respTime)
    servoX.ChangeDutyCycle(s_hold)
    #time.sleep(100*respTime)

def Up():
    print("Up")
    servoY.ChangeDutyCycle(standard+AcSpeed)
    time.sleep(respTime)
    servoY.ChangeDutyCycle(s_hold)
    #time.sleep(100*respTime)

def Down():
    print("Down")
    servoY.ChangeDutyCycle(standard-AcSpeed)
    time.sleep(respTime)
    servoY.ChangeDutyCycle(s_hold)
    #time.sleep(100*respTime)

if __name__ == '__main__':
    threshold = 80
    
    URL = "http://localhost:8080/?action=stream"

    #Set color for face detection
    rectangle_color = (0, 0, 255) #緑色
    #Prepare Video stream
    video = cv2.VideoCapture(URL)
    video.set(7,FPS)
    videoW = video.get(3)
    videoH = video.get(4)

    print(videoW)
    print(videoH)

    #Prepare cascade classifier by trained model
    cascade_path = 'haarcascade_frontalface_default.xml'
    cascade = cv2.CascadeClassifier(cascade_path)

    #Flag for tracker
    initBB = None
    #set up tracler By KCF algorithm
    tracker = cv2.TrackerKCF_create()

while video.isOpened():
    #read video frame
    for i in range(FPS): ret, frame = video.read()
    #if video frame dosent exist, break
    if not ret: break
    #when tracking is not on
    if initBB is None:
        facerect = cascade.detectMultiScale(frame, scaleFactor=1.3, minNeighbors=2, minSize=(10, 10))
        # when face detected
        if len(facerect) > 0:
            initBB = (facerect[0][0],facerect[0][1],facerect[0][0]+facerect[0][2]/5,facerect[0][1]+facerect[0][3]/2)
            print("Detected!:")
            print(initBB)
            tracker = cv2.TrackerKCF_create()
            tracker.init(frame, initBB)
            
            for rect in facerect:
                cv2.rectangle(frame, tuple(rect[0:2]),tuple(rect[0:2] + rect[2:4]), rectangle_color, thickness=2)
                # 顔部分の抽出
                #cut_frame = frame[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]
                # サイズの縮小
                #cut_frame = cv2.resize(cut_frame,(rect[2]//20, rect[3]//20))
                # 元のサイズにリサイズ。
                # cv2.INTER_NEAREST（最近傍補間）オプションを指定することで荒くなる。デフォルトでは cv2.INTER_LINEAR（バイリニア補間）となり、滑らかなモザイクとなる。
                #cut_frame = cv2.resize(cut_frame,(rect[2], rect[3]),cv2.INTER_NEAREST)
                # 縮小→復元画像で元の画像と置換
                #frame[rect[1]:rect[1]+rect[3],rect[0]:rect[0]+rect[2]]=cut_frame
    #when tracking is on
    else:
        (success, box) = tracker.update(frame)
        # check to see if the tracking was a success
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h),(0, 255, 0), 2)
            #Calculate positon
            print("coordinate:")
            print((x,y,w,h))

            #move servo motor
            print(videoW - x+w/2)
            print(videoH - y+h/2)
            if videoW - (x + w/2) < threshold:
                threadL = threading.Thread(target=Right)
                threadL.start()
                #pL = Process(target=Left,args=(servoX,standard+AcSpeed,s_hold,respTime))
                #pL.start()
                #Right()
            elif videoW - (x + w/2) > videoW - threshold:
                threadR = threading.Thread(target=Left)
                threadR.start()
                #pR = Process(target=Right)
                #pR.start()
                #Left()

            if videoH - (y + h/2) < threshold:
                threadU = threading.Thread(target=Up)
                threadU.start()
                #pU = Process(target=Up)
                #pU.start()
                #Up()

            elif videoH - (y + h/2) > videoH - threshold:
                threadD = threading.Thread(target=Down)
                threadD.start()
                #pD = Process(target=Down)
                #pD.start()
                #Down()
        else:
            print("-------Lost Target--------")
            initBB = None
            
    # フレームの描画
    #thread1 = threading.Thread(target=cv2.imshow('frame', frame))
    #thread1.start()
    #cv2.imshow('frame', frame)
    
    #cv2.waitKey() & 0xff
    
#メモリの解放
video.release()
cv2.destroyAllWindows()
