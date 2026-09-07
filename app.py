# app.py

from flask import Flask, render_template, request, send_from_directory, url_for
import os
import json
import uuid
import numpy as np
import tensorflow as tf
from werkzeug.utils import secure_filename


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "plant_disease_recog_model_pwp.keras"
)

JSON_PATH = os.path.join(
    BASE_DIR,
    "plant_disease.json"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploadimages"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


ALLOWED_EXTENSIONS = {
    "jpg",
    "jpeg",
    "png"
}


# ============================================================
# 39 LABELS
# ============================================================

LABELS = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Background_without_leaves",
    "Blueberry___healthy",
    "Cherry___Powdery_mildew",
    "Cherry___healthy",
    "Corn___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn___Common_rust",
    "Corn___Northern_Leaf_Blight",
    "Corn___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading model:")
print(MODEL_PATH)

model = tf.keras.models.load_model(MODEL_PATH)

print("Model loaded successfully!")
print("Model input shape:", model.input_shape)
print("Model output shape:", model.output_shape)
print("Number of labels:", len(LABELS))


if model.output_shape[-1] != len(LABELS):
    raise ValueError(
        f"Model has {model.output_shape[-1]} classes "
        f"but LABELS contains {len(LABELS)} labels."
    )


# ============================================================
# LOAD JSON
# ============================================================

plant_disease = {}

if os.path.exists(JSON_PATH):
    try:
        with open(
            JSON_PATH,
            "r",
            encoding="utf-8"
        ) as file:
            plant_disease = json.load(file)

        print("plant_disease.json loaded.")

    except Exception as e:
        print("Could not load plant_disease.json:")
        print(e)


# ============================================================
# CHECK IMAGE
# ============================================================

def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def prepare_image(image_path):

    image = tf.keras.utils.load_img(
        image_path,
        target_size=(160, 160),
        color_mode="rgb"
    )

    image_array = tf.keras.utils.img_to_array(image)

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    return image_array


# ============================================================
# PREDICTION
# ============================================================

def model_predict(image_path):

    image_array = prepare_image(image_path)

    prediction = model.predict(
        image_array,
        verbose=0
    )

    prediction = np.asarray(prediction)

    predicted_index = int(
        np.argmax(prediction[0])
    )

    confidence = float(
        np.max(prediction[0])
    ) * 100

    predicted_label = LABELS[predicted_index]

    print("Prediction:", predicted_label)
    print("Confidence:", confidence)

    return predicted_label, confidence


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template(
        "home.html"
    )


# ============================================================
# UPLOADED IMAGE
# ============================================================

@app.route(
    "/uploadimages/<path:filename>"
)
def uploaded_images(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# ============================================================
# UPLOAD
# ============================================================

@app.route(
    "/upload/",
    methods=["GET", "POST"]
)
def uploadimage():

    if request.method == "GET":

        return render_template(
            "home.html"
        )


    if "img" not in request.files:

        return render_template(
            "home.html",
            error="No image was uploaded.",
            result=False
        )


    image = request.files["img"]


    if image.filename == "":

        return render_template(
            "home.html",
            error="No image was selected.",
            result=False
        )


    if not allowed_file(image.filename):

        return render_template(
            "home.html",
            error="Please upload a JPG, JPEG or PNG image.",
            result=False
        )


    filename = secure_filename(
        image.filename
    )


    extension = os.path.splitext(
        filename
    )[1].lower()


    unique_filename = (
        "plant_"
        + uuid.uuid4().hex
        + extension
    )


    image_path = os.path.join(
        UPLOAD_FOLDER,
        unique_filename
    )


    try:

        image.save(image_path)

        prediction, confidence = model_predict(
            image_path
        )

        image_url = url_for(
            "uploaded_images",
            filename=unique_filename
        )

        return render_template(
            "home.html",
            result=True,
            imagepath=image_url,
            prediction=prediction,
            confidence=round(confidence, 2)
        )


    except Exception as e:

        print("Prediction error:", e)

        return render_template(
            "home.html",
            result=False,
            error=str(e)
        )


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
        use_reloader=False
    )