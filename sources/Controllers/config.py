PORT = 8001
CONF_CONTENT_THRESHOLD = 0.7
IOU_CONTENT_THRESHOLD = 0.7

# CONF_CORNER_THRESHOLD = 0.8
# IOU_CORNER_THRESHOLD = 0.5

CORNER_MODEL_PATH = "sources/Database/OCR/weights/corner.pt"
CONTENT_MODEL_PATH = "sources/Database/OCR/weights/content.pt"
FACE_MODEL_PATH = "sources/Database/OCR/weights/face.pt"
# OCR_MODEL_PATH = "sources/Database/OCR/weights/seq2seq.pth"
# OCR_CFG = 'sources/Database/OCR/config/seq2seq_config.yml'
DEVICE = "cpu"  # or "cuda:0" if using GPU

# Config directory
UPLOAD_FOLDER = "sources/Database/uploads"
id_card_parts = "sources/static/images_collected/id_card_parts"
face_crop_verify = "sources/static/images_collected/face_crop_verify"
face_liveness = "sources/static/images_collected/face_liveness"
