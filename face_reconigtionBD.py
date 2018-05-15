# Import OpenCV2 for image processing
import cv2
import MySQLdb
# Import numpy for matrices calculations

import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time


def getProfile(id):
    db = MySQLdb.connect(host="192.168.1.4", user="student", passwd="student", db="demo")
    cur = db.cursor()
    cur.execute("SELECT * FROM demo.employees WHERE id="+str(id))
    profile= None
    for row in cur:
        profile=row
    # close the cursor
    cur.close()

    # close the connection
    db.close()
    return  profile



# Create Local Binary Patterns Histograms for face recognization
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Load the trained mode
recognizer.read('trainer/trainer.yml')


# Load prebuilt model for Frontal Face
cascadePath = "/home/pi/opencv-3.4.0/data/haarcascades/haarcascade_frontalface_default.xml"

# Create classifier from prebuilt model
face_cascade = cv2.CascadeClassifier(cascadePath);

# Set the font style
font = cv2.FONT_HERSHEY_SIMPLEX

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup
time.sleep(0.1)


for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	
    image = frame.array
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    for (x,y,w,h) in faces:
    # Create rectangle around the face
        cv2.rectangle(image, (x-20,y-20), (x+w+20,y+h+20), (0,255,0), 4)

    # Recognize the face belongs to which ID
        #Id = recognizer.predict(gray[y:y+h,x:x+w])
        Id, conf = recognizer.predict(gray[y:y+h,x:x+w])
        print(conf)
        cv2.rectangle(image, (x - 22, y - 90), (x + w + 22, y - 22), (255, 0, 0), -1)
        profile = getProfile(Id)


    # Check the ID if exist 
        #if(Id == 1):
            #Id = "Trompe"
        #If not exist, then it is Unknown
        #elif(Id == 2):
            #Id = "Jenifer"
        #else:
            #print(Id)
            #Id = "Unknow"

        # Put text describe who is in the picture
        
        cv2.putText(image, str(profile[1]), (x,y-40), font, 2, (255,255,255), 3)
        cv2.putText(image, str(profile[2]), (x, y + 30), font, 2, (255, 255, 255), 3)

    # Display the video frame with the bounded rectangle
    cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF
 
	# clear the stream in preparation for the next frame
    rawCapture.truncate(0)
 
	# if the `q` key was pressed, break from the loop
    if key == ord("q"):
	    break
	
cv2.destroyAllWindows()
