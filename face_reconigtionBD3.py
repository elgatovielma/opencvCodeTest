# Import OpenCV2 for image processing
import cv2
import MySQLdb
# Import numpy for matrices calculations

import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import threading
import RPi.GPIO as GPIO
import requests


# GPIO SETUP


Pin_Known_Person = 18
Pin_Unknown_Person = 24
Pin_Button = 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Pin_Known_Person, GPIO.OUT)
GPIO.setup(Pin_Unknown_Person, GPIO.OUT)
GPIO.setup(Pin_Button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Create Local Binary Patterns Histograms for face recognization
recognizer = cv2.face.LBPHFaceRecognizer_create()


# Load prebuilt model for Frontal Face
cascadePath = "/home/pi/opencv-3.4.0/data/haarcascades/haarcascade_frontalface_default.xml"

# Create classifier from prebuilt model
face_cascade = cv2.CascadeClassifier(cascadePath)

# Set the font style
font = cv2.FONT_HERSHEY_SIMPLEX

camera = PiCamera()
camera.resolution = (1280, 720)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(1280, 720))

# allow the camera to warmup
time.sleep(0.1)


def getProfile(id):
    # db = MySQLdb.connect(host="192.168.1.11", user="root", passwd="", db="tesis")
    db = MySQLdb.connect(host="192.168.1.4", user="student", passwd="student", db="demo")
    cur = db.cursor()
    # cur.execute("SELECT * FROM tesis.empleados WHERE id=" + str(id))
    cur.execute("SELECT * FROM demo.employees WHERE id=" + str(id))
    profile = None
    for row in cur:
        profile = row
    # close the cursor
    cur.close()

    # close the connection
    db.close()
    return profile


def sistemaReconocimiento():
    # Validation for being sure it's an unknown user
    counter_validation = 0
    inicio = time.time()
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        
        image = frame.array
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        for (x, y, w, h) in faces:
            # Create rectangle around the face
            cv2.rectangle(image, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 255, 0), 4)

            # Recognize the face belongs to which ID
            # Id = recognizer.predict(gray[y:y+h,x:x+w])
            Id, conf = recognizer.predict(gray[y:y + h, x:x + w])
            print(conf)
            print(Id)
            cv2.rectangle(image, (x - 22, y - 90), (x + w + 22, y - 22), (255, 0, 0), -1)
            if conf < 52:
                counter_validation = 0
                profile = getProfile(Id)

                # if not t.is_alive():
                # t.start()
                GPIO.output(Pin_Unknown_Person, GPIO.LOW)
                GPIO.output(Pin_Known_Person, GPIO.HIGH)

                # Put text describe who is in the picture

                cv2.putText(image, str(profile[1]), (x, y - 40), font, 2, (255, 255, 255), 3)
                cv2.putText(image, str(profile[2]), (x, y + 120), font, 2, (255, 255, 255), 3)
                cv2.putText(image, str(profile[3]), (x, y + 200), font, 2, (255, 255, 255), 3)
            else:
                Id = "Unknown"
                cv2.rectangle(image, (x - 22, y - 90), (x + w + 22, y - 22), (255, 0, 0), -1)
                cv2.putText(image, str(Id), (x, y - 40), font, 2, (255, 255, 255), 3)
                counter_validation += 1
                print("counter: " + str(counter_validation))
                if counter_validation == 4:
                    GPIO.output(Pin_Known_Person, GPIO.LOW)
                    GPIO.output(Pin_Unknown_Person, GPIO.HIGH)
                    r = requests.get('http://192.168.1.4/pruebaBD/push_notification.php')
                    #r = requests.get('http://192.168.1.11/tesis/push_notification.php')
                    counter_validation = 0

        # Display the video frame with the bounded rectangle
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF

        fin = time.time() - inicio

        # clear the stream in preparation for the next frame
        rawCapture.truncate(0)

        # if the `q` key was pressed, break from the loop
        if key == ord("q") or fin > 30:
            GPIO.output(Pin_Known_Person, GPIO.LOW)
            GPIO.output(Pin_Unknown_Person, GPIO.LOW)
            break

    cv2.destroyAllWindows()




while True:
    entrada = GPIO.input(Pin_Button)
    if entrada == False:
        # Load the trained mode
        recognizer.read('trainer/trainer.xml')
        print('Button Pressed')
        sistemaReconocimiento()
        
