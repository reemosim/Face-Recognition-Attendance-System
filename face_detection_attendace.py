from ctypes import sizeof
import pandas as pd
import cv2
import urllib.request
import numpy as np
import os
from datetime import datetime
import face_recognition
import requests
from io import BytesIO

path = r'C:/Users/96650/Desktop/ATTENDANCE/image_folder'
url = "http://192.168.0.135:81/stream"
res = requests.get(url, stream=True)
images = []
classNames = []
classSID = []
studentInfo = {441500200: 'ellon musk',431500200: 'mohamad', 441500243: 'priyansh', 441500240:'reem', 341500200: 'usain bolt'}

if 'Attendance.csv' in os.listdir(os.path.join(os.getcwd(), 'students')):
    print("there iss..")
    os.remove("Attendance.csv")
else:
    df = pd.DataFrame(list())
    df.to_csv("Attendance.csv")
myList = os.listdir(path)

#print images names with extension
print(myList)
for i in studentInfo:
    classNames.append(studentInfo[i])
    classSID.append(i)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    # classNames.append(os.path.splitext(cl)[0])
print(classNames)
print(classSID)
#-----------------------------------------------------------------------
#encode\Analyze images stored
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
#-----------------------------------------------------------------------
def markAttendance(name):
    with open("Attendance.csv", 'r+') as f:
        f1 = f.read()
        if name not in f1:
            now = datetime.now()
            dtString = now.strftime('%H:%M')
            for i in studentInfo:
                if name == studentInfo[i]:
                    ID = i
            f.writelines(f'\n{name},{dtString},{ID}')
#-----------------------------------------------------------------------
#add attendance in sheet
#def markAttendance(name):
#   with open("Attendance.csv",'r+') as f:
#        f1=f.read()
#        if name not in f1:    
#               now = datetime.now()
#               dtString = now.strftime('%H:%M:%S')
#               f.writelines(f'\n{name},{dtString}')


encodeListKnown = findEncodings(images)
print('Encoding Complete')

#open the camera
for chunk in res.iter_content(chunk_size=120000):
    if len(chunk) > 100:
        try:
            img_resp = BytesIO(chunk)
            imgnp = np.frombuffer(img_resp.read(), np.uint8)
            img = cv2.imdecode(imgnp, 1)
            imgS = cv2.resize(img, (0, 0), None, 1, 1)
            imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
            #recognize images from camera
            facesCurFrame = face_recognition.face_locations(imgS)
            encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
            #comparing : images vs camera
            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
                faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
                matchIndex = np.argmin(faceDis)
                #green square
                if matches[matchIndex]:
                    name = classNames[matchIndex]#.upper()
                    y1, x2, y2, x1 = faceLoc
                    y1, x2, y2, x1 = y1 * 1, x2 * 1, y2 * 1, x1 * 1
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.rectangle(img, (x1, y2 - 35), (x2, y2),(0, 255, 0), cv2.FILLED)
                    cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                    markAttendance(name)
            #Window of camera: size & name
            cv2.namedWindow("Face", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Face", 700, 500)
            cv2.imshow("Face", img)
            key = cv2.waitKey(5)
            if key == ord('q'):
                break
        except Exception as e:
            print(str(e))
            continue
cv2.destroyAllWindows()
#cv2.destroyWindow('Face')
cv2.imread
