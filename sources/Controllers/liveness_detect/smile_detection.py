import cv2 as cv
import dlib
import numpy as np
from imutils import face_utils

class SmileDetector():
    def predict(self,landmarks):
        #calculate the lips width
        left_lip_edge = landmarks[48]
        right_lip_edge = landmarks[54] 

        lips_width = np.abs(left_lip_edge[0]-right_lip_edge[0])    
        face_width = np.abs(landmarks[3][0] - landmarks[13][0])   
        return  lips_width/face_width >= 0.45 # if true then is smile

