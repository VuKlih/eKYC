import torch
import numpy as np
import dlib
import cv2 as cv
import os
import matplotlib.pyplot as plt

class FaceOrientationDetector():
    """This class detects the orientation of a face in an image."""
    def __init__(self):
        self.frontal_range = [25, 60] # fine tune this range veify face turn left or right

    def calculate_angle(self, v1, v2):
        '''
        Calculate the angle between 2 vectors v1 and v2
        '''
        if isinstance(v1, torch.Tensor):
            v1 = v1.numpy()
        else:
            v1 = np.array(v1)
        if isinstance(v2, torch.Tensor):
            v2 = v2.numpy()
        else:
            v2 = np.array(v2)
            
        cosine = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        rad = np.arccos(cosine)
        degrees = np.degrees(rad)
        
        return np.round(degrees)

    # def detect(self, landmarks, img):
    def detect(self, landmarks):
        '''
        Detects the orientation of a face based on landmarks.
        '''
        left_eye = np.mean(landmarks[36:42], axis=0)
        right_eye = np.mean(landmarks[42:48], axis=0)
        nose = np.mean(landmarks[30:36], axis=0)
        
        left2right_eye = right_eye - left_eye
        lefteye2nose = nose - left_eye
        
        left_angle = self.calculate_angle(left2right_eye, lefteye2nose)
        
        right2left_eye = left_eye - right_eye
        righteye2nose = nose - right_eye
        
        right_angle = self.calculate_angle(right2left_eye, righteye2nose)
        
        print("right_angle:", right_angle)
        print("left_angle:", left_angle)

        # # Draw vectors
        # cv.line(img, tuple(left_eye.astype(int)), tuple(nose.astype(int)), (255, 0, 0), 2)
        # cv.line(img, tuple(right_eye.astype(int)), tuple(nose.astype(int)), (0, 255, 0), 2)
        # cv.line(img, tuple(left_eye.astype(int)), tuple(right_eye.astype(int)), (0, 0, 255), 2)
        
        # # Annotate angles
        # cv.putText(img, f"{left_angle}", tuple(left_eye.astype(int)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        # cv.putText(img, f"{right_angle}", tuple(right_eye.astype(int)), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        if self.frontal_range[0] <= left_angle <= self.frontal_range[1] \
            and self.frontal_range[0] <= right_angle <= self.frontal_range[1]:
                return 'front'
            
        elif left_angle > right_angle:
            return 'left'
        
        return 'right'

shape_predictor_path = "D:/Intern/AI/eKYC/eKYC/liveness_detection/shape_predictor_68_face_landmarks.dat"
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(shape_predictor_path)

def get_landmarks(image_path):
    print("Processing image:", image_path)
    img = cv.imread(image_path)

    if img is None:
        print(f"Failed to load image at {image_path}")
        return None, None

    detected_faces = detector(img, 1)

    if len(detected_faces) > 0:
        shape = sp(img, detected_faces[0])
        landmarks = np.array([[p.x, p.y] for p in shape.parts()])
        return landmarks, img
    else:
        print("No faces detected in the image.")
        return None, None

# if __name__ == '__main__':
#     new_img_name = r"D:\Intern\AI\eKYC\eKYC\liveness_detection\WIN_20240710_10_09_33_Pro.jpg"
#     landmarks, img = get_landmarks(new_img_name)
    
#     if landmarks is not None:
#         # Visualize landmarks
#         for (x, y) in landmarks:
#             cv.circle(img, (x, y), 1, (0, 0, 255), -1)
        
#         face_orien = FaceOrientationDetector()
#         orien = face_orien.detect(landmarks, img)
#         print("Detected orientation:", orien)
        
#         # Show the image with annotations
#         plt.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
#         plt.title(f"Detected orientation: {orien}")
#         plt.show()
