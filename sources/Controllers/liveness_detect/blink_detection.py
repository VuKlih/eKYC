import dlib
import cv2 as cv
import numpy as np
from imutils import face_utils
import os
import math

class BlinkDetector():
    '''A class for detecting eye blinking in facial images'''
    
    def __init__(self):
        self.EYE_AR_THRESH = 0.25
        self.EYE_AR_CONSEC_FRAMES = 3
        self.counter = 0
        self.total = 0

    def eye_blink(self, shape, thresh=3):
        '''
        Detects eye blinking in a given face region of an input BGR image.

        Parameters:
        - shape: Facial landmarks as a numpy array.
        - thresh (int): A challenge-response threshold that the user needs to surpass.

        Returns:
        - out (bool): True if the user successfully surpasses the challenge (>= thresh), False otherwise (< thresh).
        '''
        leftEye = shape[36:42]
        rightEye = shape[42:48]
        leftEAR = self.eye_aspect_ratio(leftEye)
        rightEAR = self.eye_aspect_ratio(rightEye)
        
        ear = (leftEAR + rightEAR) / 2.0
        if ear < self.EYE_AR_THRESH:
            self.counter += 1
        else:
            if self.counter >= self.EYE_AR_CONSEC_FRAMES:
                self.total += 1
            self.counter = 0
        
        if self.total >= thresh:
            return True
        
        return False

    def eye_aspect_ratio(self, eye):
        A = math.dist(eye[1], eye[5])
        B = math.dist(eye[2], eye[4])
        C = math.dist(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

shape_predictor_path = "sources/Database/shape_predictor_68_face_landmarks_GTX.dat"  # Update this path
face_rec_model_path = "sources/Database/dlib_face_recognition_resnet_model_v1.dat"  # Update this path

detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(shape_predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)

# if __name__ == '__main__':
#     camera = cv.VideoCapture(0)
#     blink_detector = BlinkDetector()
#     isCorrect = False
    
#     while True:
#         _, image = camera.read()
#         image = cv.flip(image, 1)
#         gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
#         rects = detector(gray, 0)
        
#         for (i, rect) in enumerate(rects):
#             shape = sp(gray, rect)
#             shape = face_utils.shape_to_np(shape)

#             for (x, y) in shape:
#                 cv.circle(image, (x, y), 2, (0, 255, 0), -1)
            
#             isCorrect = blink_detector.eye_blink(shape)

#             if isCorrect:
#                 cv.putText(image, "Blink 3 times successfully", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
#                 break
#             else:
#                 cv.putText(image, "Fail blink challenge", (10, 30), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

#         cv.imshow("Output", image)
#         if isCorrect:  # Exit the main loop if the user has blinked 3 times
#             break
#         k = cv.waitKey(5) & 0xFF
#         if k == ord('q'):
#             break

#     cv.destroyAllWindows()
#     camera.release()
