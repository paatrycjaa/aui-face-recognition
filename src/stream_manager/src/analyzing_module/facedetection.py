from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
from keras_vggface.utils import decode_predictions
import mtcnn
import cv2
import numpy as np


REQUIRED_SIZE = (224,224)

class FaceDetection:

    def __init__(self, opencv = False, identification = True):
        self._detector = None
        self._opencv = opencv
        self._identification = identification
        if self._opencv:
            self._detector = cv2.CascadeClassifier('analyzing_module/haarcascade_frontalface_default.xml')
        else:
            self._detector = mtcnn.MTCNN()
        if self._identification == True:
            self._classificator = VGGFace(model='resnet50')
        else:
            self._classificator = None

    def _find_faces(self, frame):
        if self._opencv: 
            results = self._detector.detectMultiScale(frame)
            res = []
            for result in results:
                x1, y1, width, height = result
                res.append([x1, y1, width, height, None])
            results = res
        else:
            results = self._detector.detect_faces(frame)
            res = []
            for result in results:
                x1 = result['box'][0]
                y1 = result['box'][1]
                width = result['box'][2]
                height = result['box'][3]
                res.append([x1, y1, width, height, None])
            results = res
        return results
    
    def _extract_faces(self, frame, results):
        faces = []
        for result in results :
            x1 = result[0]
            y1 = result[1]
            x2 = x1 + result[2]
            y2 = y1 + result[3]
            face = cv2.resize(frame[y1:y2, x1:x2], REQUIRED_SIZE)
            faces.append(face)
        
        return faces

    def _recognize_face(self, faces):

        faces = np.array(faces)
        faces = faces.astype('float32')
        #faces = np.expand_dims(faces, axis=0)
        faces = preprocess_input(faces)
        prediction = self._classificator.predict(faces)

        return decode_predictions(prediction)
    
    def _choose_right_predictions(self, predictions) :
        labels = []
        for predict in predictions:
            top_one = predict[0]
            if top_one[1] > 0.5 :
                label = f'{top_one[0]} : {top_one[1]}'
            else :
                label = f'?'
            labels.append(label)
        return labels
    
    def draw_bounding_boxes(self, frame, results):
        if results is None:
            return
        for result in results:
            x1, y1, width, height = result[:4]

            x2 = x1 + width
            y2 = y1 + height
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255))
    
    def perform_face_detection(self, frame):

        results = self._find_faces(frame)
        self.draw_bounding_boxes(frame,results)
        if self._identification == True :
            faces = self._extract_faces(frame, results)
            predictions = self._recognize_face(faces)
            labels = self._choose_right_predictions(predictions)
            results = self._concatanate_results(labels, results)
        
        return results
    
    def _concatanate_results(self, labels, results):
        for i, result in enumerate(results):
            result[4] = labels[i]
        return results


if __name__ == "__main__":

    test_pic = "analyzing_module/src/test1.jpg"
    image = cv2.imread(test_pic)
    print(type(image))
    faceRecogntion = FaceDetection(opencv=False, identification=True)
    postImage = faceRecogntion.perform_face_detection(image)
    cv2.imshow('tytul', postImage)
    cv2.waitKey(0)