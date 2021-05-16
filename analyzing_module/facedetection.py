from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
from keras_vggface.utils import decode_predictions
import mtcnn
import cv2
import numpy as np


class FaceDetection:

    def __init__(self):
        self.detector = mtcnn.MTCNN()
        self.classificator = VGGFace(model='resnet50')

    def get_embedding(self, faces):

        for face in faces:
            face = preprocess_input(face)
            prediction = self.classificator.predict(face)
            print('Predicted:', decode_predictions(prediction))

    
    def extract_face(self, frame, required_size =(224,224)):
        results = self.detector.detect_faces(frame)
        faces = []

        for result in results:
            x1 = result['box'][0]
            y1 = result['box'][1]
            width = result['box'][2]
            height = result['box'][0]

            x2 = x1 + width
            y2 = y1 + height

            cv2.rectangle(frame,(x1, y1),(x2, y2),(0, 0, 255))
            face = cv2.resize(frame[y1:y2, x1:x2], required_size)
            faces.add(face)

        return frame


