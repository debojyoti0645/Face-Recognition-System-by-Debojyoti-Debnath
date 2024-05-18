import os.path
import pickle
import cvzone
import cv2
import face_recognition
import numpy as np

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage


cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recognition-2cb6c-default-rtdb.firebaseio.com/",
    'storageBucket': "face-recognition-2cb6c.appspot.com"
})

bucket = storage.bucket()

frame_width = 640
frame_height = 480

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)

imgBackground = cv2.imread('Resources/Background .jpg')

folderModePath = 'Resources/mode'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

if not cap.isOpened():
    print("Could not open the webcam.")
    exit()

print("Loading Encode file...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, ids = encodeListKnownWithIds
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

while True:
    ret, frame = cap.read()

    imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = frame
    imgBackground[99:99 + 550, 838:838 + 390] = imgModeList[modeType]

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = ids[matchIndex]


            if counter ==0:
                counter = 1
                modeType = 1

    if counter!= 0:

        if counter ==1:
            studentInfo = db.reference(f'Students/{id}').get()
            print(studentInfo)

            blob = bucket.get_blob(f'Img/{id}.jpg')
            array = np.frombuffer(blob.download_as_string(), np.uint8)
            imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

            ref = db.reference(f'Students/{id}')


        if counter<=10:
            cv2.putText(imgBackground, str(studentInfo['ID']), (890, 139), cv2.FONT_HERSHEY_COMPLEX, 0.6, (55, 55, 55), 2)

            (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 0.8, 2)
            offset = (390 - w) // 2
            cv2.putText(imgBackground, str(studentInfo['name']), (900, 350), cv2.FONT_HERSHEY_COMPLEX, 0.8, (55, 55, 55), 2)

            cv2.putText(imgBackground, str(studentInfo['Age']), (900, 400), cv2.FONT_HERSHEY_COMPLEX, 1, (55, 55, 55), 2)

            cv2.putText(imgBackground, str(studentInfo['Gender']), (900, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (55, 55, 55), 2)

            cv2.putText(imgBackground, str(studentInfo['Address']), (900, 500), cv2.FONT_HERSHEY_COMPLEX, 1, (55, 55, 55), 2)

            imgBackground[160:160+155, 969:969+124] = imgStudent

        counter+=1

        if counter>=11:
            counter = 0
            modeType = 0
            studentInfo = []
            imgStudent = []

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    cv2.imshow("Face Recognition", imgBackground)

