import cv2
import dlib
import numpy as np
from imutils import face_utils

def get_ear(eye): # Eye Aspect Ratio
    # compute the euclidean distances between the two sets of
    # vertical eye landmarks (x, y)-coordinates
    A = np.linalg.norm(eye[1] - eye[5])
    B = np.linalg.norm(eye[2] - eye[4])
    # compute the euclidean distance between the horizontal
    # eye landmark (x, y)-coordinates
    C = np.linalg.norm(eye[0] - eye[3]) 
    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C) 
    print(ear)
    # return the eye aspect ratio
    return ear

# if __name__ == '__main__':
    # Load the pre-trained face detection model