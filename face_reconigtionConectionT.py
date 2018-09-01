
import cv2
import MySQLdb
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import threading
import RPi.GPIO as GPIO
import requests
from PIL import Image
import os, sys


# GPIO Inicio
Pin_Known_Person = 18
Pin_Unknown_Person = 24
Pin_Button = 25

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(Pin_Known_Person, GPIO.OUT)
GPIO.setup(Pin_Unknown_Person, GPIO.OUT)
GPIO.setup(Pin_Button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Confianza minima
min_conf = 42

#Crear LBPH para reconocimiento de cara
recognizer = cv2.face.LBPHFaceRecognizer_create()



#Cargar modelo previo de cara frontal
cascadePath = "/home/pi/opencv-3.4.0/data/haarcascades/haarcascade_frontalface_default.xml"

#URL
rutaImagenes = 'http://192.168.1.11/tesis/imgReceived.php'

#Crear clasificador de modelo previo
face_cascade = cv2.CascadeClassifier(cascadePath)


# Colocar el estilo de fondo
font = cv2.FONT_HERSHEY_SIMPLEX

camera = PiCamera()
camera.resolution = (1280, 720)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(1280, 720))

#Permitir a la camara iniciar
time.sleep(0.1)


#Devuelve los datos de la persona, cuyo id sea solicitado
def getProfile(id):
    db = MySQLdb.connect(host="192.168.1.11", user="root", passwd="", db="tesis_sistemadeseguridad")
    cur = db.cursor()
    cur.execute("SELECT * FROM tesis_sistemadeseguridad.empleado WHERE id=" + str(id))
    profile = None
    for row in cur:
        profile = row
    # Cerrar el cursor
    cur.close()
    # Cerrar la coneccion
    db.close()
    return profile


#Se envio la captura de la persona desconocida al sistema de ficheros
def envioImagen(img):
    cv2.imwrite("temporal/Desconocido" + ".jpg", img)
    files = {'file': open('temporal/Desconocido.jpg', 'rb')}
    r = requests.post(rutaImagenes, files=files)
    print(r.text)
    os.remove("temporal/Desconocido.jpg")


#Se hace el procedimiento de reconocer a una persona
def sistemaReconocimiento():

    counter_validation = 0
    inicio = time.time()
    
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        
        image = frame.array
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)

        for (x, y, w, h) in faces:
            # Crear un ractangulo alrededor de la cara
            cv2.rectangle(image, (x - 20, y - 20), (x + w + 20, y + h + 20), (0, 255, 0), 4)

            # Reconocer a cual id pertenece la cara
            Id, conf = recognizer.predict(gray[y:y+h,x:x+w])
            print(conf)
            print(Id)
            cv2.rectangle(image, (x - 22, y - 90), (x + w + 22, y - 22), (255, 0, 0), -1)
            #Si es menor la confianza al limite establecido se busca el usuario en la base de datos
            if conf < min_conf:
                counter_validation = 0
                #Se entra al metodo getProfile
                profile = getProfile(Id)
                conf = "  {0}%".format(round(100 - conf))

                # Colocamos texto de quien es la persona
                cv2.putText(image, str(profile[1]), (x, y - 40), font, 2, (255, 255, 255), 3)
                cv2.putText(image, str(profile[2]), (x, y + 50), font, 2, (255, 255, 255), 3)
                cv2.putText(image, str(conf), (x -60, y - 90 ), font, 2, (255, 255, 255), 3)
                if counter_validation_ok == 3:
                    GPIO.output(Pin_Unknown_Person, GPIO.LOW)
                    GPIO.output(Pin_Known_Person, GPIO.HIGH)
                    counter_validation_ok = 0
                    
            else:
                Id = "Desconocido"
                cv2.rectangle(image, (x - 22, y - 90), (x + w + 22, y - 22), (255, 0, 0), -1)
                cv2.putText(image, str(Id), (x, y - 40), font, 2, (255, 255, 255), 3)
                counter_validation += 1
                print("counter: " + str(counter_validation))
                #Si el incremento llega a la condicion establecida se entra aqui, el incremento se tiene para vitar falsos positivos
                if counter_validation == 5:
                    GPIO.output(Pin_Known_Person, GPIO.LOW)
                    GPIO.output(Pin_Unknown_Person, GPIO.HIGH)
                    #Se entra a la funcion envioImagen
                    envioImagen(gray[y:y + h, x:x + w])
                    counter_validation = 0

        #Se muestra el cuadro actual con el cuadro dibujado
        cv2.imshow("Frame", image)
        key = cv2.waitKey(1) & 0xFF

        fin = time.time() - inicio

        #Se borra el cuadro anterior para asi mostrar el siguiente
        rawCapture.truncate(0)

        #Si se oprime una tecla "q" o pasan mas de 30 segundos se sale del ciclo
        if key == ord("q") or fin > 30:
            GPIO.output(Pin_Known_Person, GPIO.LOW)
            GPIO.output(Pin_Unknown_Person, GPIO.LOW)
            break

    cv2.destroyAllWindows()




while True:
    entrada = GPIO.input(Pin_Button)
    #Se espera a que el boton sea presionado
    #if entrada == False:
        # Se carga el trainer y se entra a la funcion sistemaReconocimiento
        #recognizer.read('trainer/trainer.yml')
    time.sleep(5)
    recognizer.read('trainer/trainer.xml')
        #print('Button Pressed')
    sistemaReconocimiento()
        
