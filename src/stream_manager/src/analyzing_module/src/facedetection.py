from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
from keras_vggface.utils import decode_predictions
import mtcnn
import cv2
import numpy as np


class FaceDetection:

    def __init__(self, opencv = False, identification = True):
        self.detector = None
        self.opencv = opencv
        self.identification = identification
        if self.opencv:
            self.detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        else:
            self.detector = mtcnn.MTCNN()
        self.classificator = VGGFace(model='resnet50')

    def get_embedding(self, faces):
        pass
        for face in faces:
            face = preprocess_input(face)
            prediction = self.classificator.predict(face)
            print('Predicted:', decode_predictions(prediction))

    def draw_bounding_boxes(self, frame, results):
        if results is None:
            return
        for result in results:
            if self.opencv:
                x1, y1, width, height = result
            else:
                x1 = result['box'][0]
                y1 = result['box'][1]
                width = result['box'][2]
                height = result['box'][3]

            x2 = x1 + width
            y2 = y1 + height
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255))

    def extract_face(self, frame, required_size =(224,224)):
        results = self.find_faces(frame)
        self.draw_bounding_boxes(frame, results)
        if self.identification:
            for result in results:
                if self.opencv:
                    x1, y1, width, height = result
                else:
                    x1 = result['box'][0]
                    y1 = result['box'][1]
                    width = result['box'][2]
                    height = result['box'][3]

                x2 = x1 + width
                y2 = y1 + height
                face = cv2.resize(frame[y1:y2, x1:x2], required_size)
                recognized_face = self.recognize_face(face)
        return frame

    def find_faces(self, frame):
        print("Start detecting")
        if self.opencv: 
            results = self.detector.detectMultiScale(frame)
        else:
            results = self.detector.detect_faces(frame)
        print("Stop detecting")
        return results

    def recognize_face(self, face):
        print("Start recognizing")
        print("Start classifying")
        face = face.astype('float32')
        face = np.expand_dims(face, axis=0)
        face = preprocess_input(face)
        prediction = self.classificator.predict(face)
        print('Predicted:', decode_predictions(prediction))
        return decode_predictions(prediction)



if __name__ == "__main__":

    test_pic = "test1.jpg"
    image = cv2.imread(test_pic)
    print(type(image))
    faceRecogntion = FaceDetection(opencv=True, identification=True)
    postImage = faceRecogntion.extract_face(image)
    cv2.imshow('tytul', postImage)
    cv2.waitKey(0)


