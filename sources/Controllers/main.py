import os
from typing import Dict

# import databases
import cv2
import numpy as np
import yolov5
from fastapi import File, Request, UploadFile, Body, Form
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from PIL import Image
# from pydantic import BaseModel
# from pylibsrtp import Session
from vietocr.tool.config import Cfg
from vietocr.tool.predictor import Predictor

import sources.Controllers.config as cfg
from sources import app, templates
from sources.Controllers import utils
from sources.Controllers.face_verification import get_face_descriptor
from sources.Controllers.liveness_detect.challenge_response import *
from sources.Controllers.liveness_detect.blink_detection import BlinkDetector
from sources.Controllers.liveness_detect.face_orientation import FaceOrientationDetector
from sources.Controllers.liveness_detect.smile_detection import SmileDetector


# Init yolov5 model
CORNER_MODEL = yolov5.load(cfg.CORNER_MODEL_PATH)
CONTENT_MODEL = yolov5.load(cfg.CONTENT_MODEL_PATH)
FACE_MODEL = yolov5.load(cfg.FACE_MODEL_PATH)

# Set conf and iou threshold -> Remove overlap and low confident bounding boxes
CONTENT_MODEL.conf = cfg.CONF_CONTENT_THRESHOLD
CONTENT_MODEL.iou = cfg.IOU_CONTENT_THRESHOLD

# Config directory
UPLOAD_FOLDER = cfg.UPLOAD_FOLDER
ID_CARD_PARTS = cfg.id_card_parts
FACE_CROP_VERIFY = cfg.face_crop_verify
FACE_LIVENESS= cfg.face_liveness

""" Recognizion detected parts in ID """
config = Cfg.load_config_from_name(
    "vgg_seq2seq"
)  
# OR vgg_transformer -> acc || vgg_seq2seq -> time
# config = Cfg.load_config_from_file(cfg.OCR_CFG)
# config['weights'] = cfg.OCR_MODEL_PATH
config["cnn"]["pretrained"] = False
config["device"] = cfg.DEVICE
config["predictor"]["beamsearch"] = False
detector = Predictor(config)

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/verification")
async def root(request: Request):
    return templates.TemplateResponse("verification.html", {"request": request})

@app.get("/liveness_detection")
async def root(request: Request):
    return templates.TemplateResponse("liveness_detection.html", {"request": request})

@app.get("/complete_ekyc_process")
async def root(request: Request):
    return templates.TemplateResponse("complete.html", {"request": request})


@app.post("/uploader")
async def upload(file: UploadFile = File(...)):
    INPUT_IMG = os.listdir(UPLOAD_FOLDER)
    if INPUT_IMG is not None:
        for uploaded_img in INPUT_IMG:
            os.remove(os.path.join(UPLOAD_FOLDER, uploaded_img))

    file_location = f"./{UPLOAD_FOLDER}/{file.filename}"
    contents = await file.read()
    with open(file_location, "wb") as f:
        f.write(contents)

    # Validating file
    INPUT_FILE = os.listdir(UPLOAD_FOLDER)[0]
    if INPUT_FILE == "NULL":
        os.remove(os.path.join(UPLOAD_FOLDER, INPUT_FILE))
        error = "No file selected!"
        return JSONResponse(status_code=403, content={"message": error})
    elif INPUT_FILE == "WRONG_EXTS":
        os.remove(os.path.join(UPLOAD_FOLDER, INPUT_FILE))
        error = "This file is not supported!"
        return JSONResponse(status_code=404, content={"message": error})

    return await extract_info()

@app.post("/extract")
async def extract_info():
    """Check if uploaded image exist"""
    if not os.path.isdir(cfg.UPLOAD_FOLDER):
        os.mkdir(cfg.UPLOAD_FOLDER)

    INPUT_IMG = os.listdir(UPLOAD_FOLDER)
    if INPUT_IMG is not None:
        img = os.path.join(UPLOAD_FOLDER, INPUT_IMG[0])

    CORNER = CORNER_MODEL(img)
    # CORNER.save(save_dir='results/')
    predictions = CORNER.pred[0]
    categories = predictions[:, 5].tolist()  # Class
    if len(categories) != 4:
        error = "Detecting corner failed!"
        return JSONResponse(status_code=401, content={"message": error})
    boxes = utils.class_Order(predictions[:, :4].tolist(), categories)  # x1, x2, y1, y2
    IMG = Image.open(img)
    center_points = list(map(utils.get_center_point, boxes))

    """ Temporary fixing """
    c2, c3 = center_points[2], center_points[3]
    c2_fix, c3_fix = (c2[0], c2[1] + 30), (c3[0], c3[1] + 30)
    center_points = [center_points[0], center_points[1], c2_fix, c3_fix]
    center_points = np.asarray(center_points)
    aligned = utils.four_point_transform(IMG, center_points)
    # Convert from OpenCV to PIL format
    aligned = Image.fromarray(aligned)
    # aligned.save('res.jpg')
    # CORNER.show()

    CONTENT = CONTENT_MODEL(aligned)
    # CONTENT.save(save_dir='results/')
    predictions = CONTENT.pred[0]
    categories = predictions[:, 5].tolist()  # Class

    boxes = predictions[:, :4].tolist()

    """ Non Maximum Suppression """
    boxes, categories = utils.non_max_suppression_fast(np.array(boxes), categories, 0.7)
    boxes = utils.class_Order(boxes, categories)  # x1, x2, y1, y2
    
    if not os.path.isdir(ID_CARD_PARTS):
        os.mkdir(ID_CARD_PARTS)
    else:
        for f in os.listdir(ID_CARD_PARTS):
            os.remove(os.path.join(ID_CARD_PARTS, f))

    for index, box in enumerate(boxes):
        left, top, right, bottom = box
        if 5 < index < 9:
            # right = c3[0]
            right = right + 100
        cropped_image = aligned.crop((left, top, right, bottom))
        cropped_image.save(os.path.join(ID_CARD_PARTS, f"{index}.jpg"))

    FIELDS_DETECTED = []  # Collecting all detected parts
    for idx, img_crop in enumerate(sorted(os.listdir(ID_CARD_PARTS))):
        if idx > 0:
            img_ = Image.open(os.path.join(ID_CARD_PARTS, img_crop))
            s = detector.predict(img_)
            FIELDS_DETECTED.append(s)

    # to concaternate the permanent residence
    if 7 in categories:
        FIELDS_DETECTED = (
                FIELDS_DETECTED[:6]
                + [FIELDS_DETECTED[6] + ", " + FIELDS_DETECTED[7]]
                + [FIELDS_DETECTED[8]]
        )

    response = {"data": FIELDS_DETECTED}
    response = jsonable_encoder(response)

    return JSONResponse(content=response)

@app.post("/correct_id_infor")
async def correct_id_infor(correct_data: Dict = Body(...)):
    response = correct_data
    print('abc:', response)
    return JSONResponse(content=response)

@app.post("/verify-face")
async def save_image(file: UploadFile = File(...)):
    file_location = os.path.join(FACE_CROP_VERIFY, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    new_img_name = f"./{FACE_CROP_VERIFY}/captured_image.jpg"
    FACE = FACE_MODEL(new_img_name)
    # left, top, right, bottom = boxes[0]
    predictions = FACE.pred[0]
    categories = predictions[:, 5].tolist()  # Class
    if 0 not in categories:
        error = "No face detected!"
        return JSONResponse(status_code=413, content={"message": error})
    elif categories.count(0) > 1:
        error = "Multiple faces detected!"
        return JSONResponse(status_code=414, content={"message": error})

    boxes = predictions[:, :4].tolist()

    """ Non Maximum Suppression """
    # boxes, categories = utils.non_max_suppression_fast(np.array(boxes), categories, 0.7)

    if not os.path.isdir(FACE_CROP_VERIFY):
        os.mkdir(FACE_CROP_VERIFY)

    FACE_IMG = Image.open(new_img_name)
    # left, top, right, bottom = boxes[0]
    cropped_image = FACE_IMG.crop((boxes[0]))
    cropped_image.save(os.path.join(FACE_CROP_VERIFY, "face_crop.jpg"))

    image_paths = [os.path.join(ID_CARD_PARTS, "0.jpg"),
                   os.path.join(FACE_CROP_VERIFY, "face_crop.jpg"),]

    distance = 0
    # Calculate face descriptors for all images
    face_descriptors = [get_face_descriptor(path) for path in image_paths]
    # Count matches and calculate percentage

    threshold = 0.6
    distance = np.linalg.norm(face_descriptors[0] - face_descriptors[1])
    verify = distance < threshold

    if verify:
        noti = "Verify successfully!"
        return JSONResponse(status_code=200, content={"message": noti, "distance": distance})
    else:
        error = "Verify failed, not similarity"
        return JSONResponse(status_code=406, content={"message": error, "distance": distance})

import json
import time
@app.post("/liveness_detect")
async def liveness_detection(file: UploadFile = File(...), challenge: str = Form(...), question:str = Form(...), ):
    start_time = time.time()
    print("Received question:", question)
    print(challenge)
    try:
        question = json.loads(question)
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"message": "Invalid question format. Expected a JSON list."})
    print(type(question))

    file_location = os.path.join(FACE_LIVENESS, file.filename)
    with open(file_location, "wb") as f:
        f.write(await file.read())
    
    new_img_name = f"./{FACE_LIVENESS}/captured_image.jpg"
    # Load the image using OpenCV
    face_img = cv2.imread(file_location)

    # Flip the image (uncomment the desired flip)
    face_img = cv2.flip(face_img, 1)  # Horizontal flip

    # Save the flipped image
    cv2.imwrite(new_img_name, face_img)

    FACE = FACE_MODEL(new_img_name)
    # left, top, right, bottom = boxes[0]
    predictions = FACE.pred[0]
    categories = predictions[:, 5].tolist()  # Class
    if 0 not in categories:
        error = "No face detected!"
        return JSONResponse(status_code=413, content={"message": error})
    elif categories.count(0) > 1:
        error = "Multiple faces detected!"
        return JSONResponse(status_code=414, content={"message": error})

    boxes = predictions[:, :4].tolist()

    """ Non Maximum Suppression """
    # boxes, categories = utils.non_max_suppression_fast(np.array(boxes), categories, 0.7)

    if not os.path.isdir(FACE_LIVENESS):
        os.mkdir(FACE_LIVENESS)

    FACE_IMG = Image.open(new_img_name)
    # left, top, right, bottom = boxes[0]
    cropped_image = FACE_IMG.crop((boxes[0]))
    cropped_image.save(os.path.join(FACE_LIVENESS, "face_crop.jpg"))

    image_paths = os.path.join(FACE_LIVENESS, "face_crop.jpg")

    # Calculate face descriptors for all images
    face_descriptors = get_face_descriptor(image_paths, landmarks_128=False) 
    
    face, box, landmarks = cropped_image, boxes[0], face_descriptors
    blink_detector = BlinkDetector()
    face_orientation_detector = FaceOrientationDetector()
    emotion_detector = SmileDetector()

    isCorrect = result_challenge_response(face, box, landmarks, challenge, question, model=[blink_detector, face_orientation_detector, emotion_detector])
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")
    
    if isCorrect:
        noti = "{liveness_challenge} challenge successfully!".format(liveness_challenge = challenge)
        return JSONResponse(status_code=200, content={"message": noti})
    else:
        error = "{liveness_challenge} challenge failed".format(liveness_challenge = challenge)
        return JSONResponse(status_code=406, content={"message": error})

 