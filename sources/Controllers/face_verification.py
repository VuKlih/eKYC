import cv2
import dlib
import numpy as np
from imutils import face_utils

# Paths for the required files
shape_predictor_path = "sources/Database/shape_predictor_68_face_landmarks_GTX.dat"  # Update this path
face_rec_model_path = "sources/Database/dlib_face_recognition_resnet_model_v1.dat"  # Update this path

# Initialize Dlib's face detector and face recognition model
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(shape_predictor_path)
facerec = dlib.face_recognition_model_v1(face_rec_model_path)

def get_face_descriptor(image_path,landmarks_128 = True):
    print("Processing image:", image_path)
    img = cv2.imread(image_path)

    if img is None:
        print(f"Failed to load image at {image_path}")
        return None

    # Detect faces
    detected_faces = detector(img, 1)

    # Process the first detected face
    if len(detected_faces) > 0:
        shape = sp(img, detected_faces[0])
        if landmarks_128 == False: 
            face_descriptor = face_utils.shape_to_np(shape)
        else:
            face_descriptor = facerec.compute_face_descriptor(img, shape)
            face_descriptor = np.array(face_descriptor)
        # print("face_descriptor:", len(face_descriptor))
        return face_descriptor
    else:
        print("No faces detected in the image.")
        return None
