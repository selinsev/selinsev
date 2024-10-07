import cv2
import time
import  numpy as np
import math
import HandTrackingModule as Htm
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


################################
wCam, hCam = 640,480
################################

cTime=0
pTime=0

detector = Htm.HandDetector(detectionCon=0.8)



devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange= volume.GetVolumeRange()
minVol= volRange[0]
maxVol = volRange[1]
vol=0
volBar=400

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
while True:
    success, frame = cap.read()
    frame = detector.findHands(frame)
    lmList= detector.findPosition(frame, draw=False)


    if len(lmList)>0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx,cy = (x1+x2)//2, (y1+y2)//2
        cv2.circle(frame, (x1,y1),10, (255,0,255), cv2.FILLED)
        cv2.circle(frame, (x2,y2),10, (255,0,255), cv2.FILLED)
        cv2.circle(frame, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
        cv2.line(frame, (x1,y1), (x2,y2), (0, 255, 0), 2)

        length= math.hypot(x2-x1, y2-y1)


        #Hand Range 30 to 130
        #Volume Range -96 to 0
        vol = np.interp(length, [30,130], [minVol,maxVol])
        volBar = np.interp(length, [30, 130], [400, 150])
        volume.SetMasterVolumeLevel(vol, None)
        print(vol)


        if length<30:
            cv2.circle(frame, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

    cv2.rectangle(frame, (50,150), (85,400), (0,255,0), 3)
    cv2.rectangle(frame, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)

    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    cv2.putText(frame, str(int(fps)), (40,90), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
    cv2.imshow('frame', frame)
    cv2.waitKey(1)

