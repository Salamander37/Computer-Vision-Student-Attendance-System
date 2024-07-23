import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import os
import csv
from io import StringIO
import pickle

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

model_path = os.path.join(r'C:\Users\user\Desktop\ceevee\models', 'ceevee.pkl')

with open(model_path, 'rb') as file:
    model = pickle.load(file)


attendance_log = set()

def load_known_faces(known_faces_dir):
    known_faces = []
    known_names = []
    for person_name in os.listdir(known_faces_dir):
        person_dir = os.path.join(known_faces_dir, person_name)
        if os.path.isdir(person_dir):
            for image_name in os.listdir(person_dir):
                image_path = os.path.join(person_dir, image_name)
                img = cv2.imread(image_path)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                for (x, y, w, h) in faces:
                    face = gray[y:y+h, x:x+w]
                    face = cv2.resize(face, (100, 100))
                    known_faces.append(face)
                    known_names.append(person_name)
    return known_faces, known_names

def recognize_faces(frame, faces, gray_frame):
    global attendance_log
    names = []
    for (x, y, w, h) in faces:
        face = gray_frame[y:y+h, x:x+w]
        face = cv2.resize(face, (100, 100)).flatten()
        name = model.predict([face])[0]
        names.append(name)
        attendance_log.add(name)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)
    return frame, names


def generate_frames():
    video_capture = cv2.VideoCapture(0)
    while True:
        success, frame = video_capture.read()
        if not success:
            break
        else:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray_frame, 1.1, 4)
            frame, names = recognize_faces(frame, faces, gray_frame)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    video_capture.release()