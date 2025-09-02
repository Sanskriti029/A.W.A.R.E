from flask import Flask, request, jsonify, render_template, send_from_directory
from PIL import Image
import numpy as np
import tensorflow as tf
from flask_cors import CORS
import subprocess
from dotenv import load_dotenv
import requests
import os
import base64
import io

# Load environment variables
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = Flask(__name__)
CORS(app)  # Enable CORS

# Load pre-trained MobileNetV2 model
model = tf.keras.applications.MobileNetV2(weights='imagenet')
target_size = (224, 224)

# ===== Helper function to classify image using MobileNetV2 =====
def predict_image(image: Image.Image) -> str:
    # Resize and preprocess image
    img_resized = image.resize(target_size)
    img_array = tf.keras.preprocessing.image.img_to_array(img_resized)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

    # Predict
    preds = model.predict(img_array)
    decoded = tf.keras.applications.mobilenet_v2.decode_predictions(preds, top=1)
    label = decoded[0][0][1]  # get class label
    return label


# ===== Home Route =====
@app.route("/")
def home():
    return render_template("index.html")  # Make sure index.html is in 'templates' folder


# ===== Predict Route =====
@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    img = Image.open(file.stream).convert("RGB")
    prediction = predict_image(img)

    # Optional: Call Google Vision API for additional labels
    try:
        url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_API_KEY}"

        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        payload = {
            "requests": [
                {
                    "image": {"content": img_str},
                    "features": [{"type": "LABEL_DETECTION", "maxResults": 3}]
                }
            ]
        }

        response = requests.post(url, json=payload)
        google_result = response.json()

    except Exception as e:
        google_result = {"error": str(e)}

    return jsonify({
        "prediction": prediction,
        "google_analysis": google_result
    })


# ===== Classify Route (placeholder) =====
@app.route("/classify", methods=["POST"])
def classify():
    return jsonify({"message": "Classification complete!"})


# ===== Soil Analysis Route =====
# @app.route("/soil-analysis", methods=["POST"])
# def soil_analysis():
#     data = request.json
#     ph = data.get("pH")
#     potash = data.get("potashLevel")

#     if ph is None or potash is None:
#         return jsonify({"error": "Missing input values"}), 400

#     try:
#         exe = "./soil_analysis" if os.name != "nt" else "soil_analysis.exe"
#         result = subprocess.check_output([exe], input=f"{ph} {potash}\n", text=True)
#         return jsonify({"result": result.strip()})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# ===== Run App =====
if __name__ == "__main__":
    app.run(debug=True)
