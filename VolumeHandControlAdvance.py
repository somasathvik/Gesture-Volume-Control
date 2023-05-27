import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam,hCam = 640,480

cap=cv2.VideoCapture(0)
cap.set(3,wCam) # 3 refers to the width of the module
cap.set(4,hCam)
pTime = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)

######### pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
########

vol=0
volforbar=400
volforper=0

while True:
    success,img = cap.read()
    img = detector.findHands(img)
    lmList, bbox=detector.findPosition(img, draw=True)
    if len(lmList)!=0:
        #print(lmList[4],lmList[8])
        #Filter based on size
        area = (bbox[2]-bbox[0]) * (bbox[3]-bbox[1])//100
        if 250 < area < 1000:
            #Find distance between index and thumb
            length, img, lineinfo = detector.findDistance(4,8,img)

            #Convert Volume
            #vol = np.interp(length,[50,300],[minVol,maxVol])
            volforbar = np.interp(length, [50, 200], [400, 150])
            volforper = np.interp(length, [50, 200], [0,100])

            #Reduce resolution to make it smoother
            smoothness = 10
            volforper = smoothness*round(volforper/smoothness)
            #volume.SetMasterVolumeLevel(vol, None)
            volume.SetMasterVolumeLevelScalar(volforper/100,None)

            if length<50:
                cv2.circle(img, (lineinfo[4],lineinfo[5]),15, (0, 255, 0), cv2.FILLED)

            cv2.rectangle(img,(50,150),(85,400),(255, 0, 0),3)
            cv2.rectangle(img, (50, int(volforbar)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, f'FPS: {int(volforper)}', (40, 450), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 3)
            cVol = int(volume.GetMasterVolumeLevelScalar()*100)
            cv2.putText(img, f'Vol Set: {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 3)


    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img,f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 3)

    cv2.imshow("Img",img)
    cv2.waitKey(1)