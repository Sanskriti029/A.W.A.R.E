from flask import Flask, request, jsonify, render_template
from PIL import Image
import numpy as np
import tensorflow as tf
import subprocess
import os

app = Flask(__name__)

# MobileNetV2 for AI classifier
model = tf.keras.applications.MobileNetV2(weights='imagenet')
target_size = (224, 224)

waste_mapping = {
    "bottle": "Plastic",
    "can": "Metal",
    "jar": "Glass",
    "banana": "Organic",
    "apple": "Organic",
    "newspaper": "Paper",
    "battery": "Battery"
}

@app.route("/")
def home():
    return render_template("index.html")


# ===== AI Classifier =====
@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    try:
        img = Image.open(file).convert("RGB")
        img = img.resize(target_size)
        x = np.array(img)
        x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
        x = np.expand_dims(x, axis=0)

        preds = model.predict(x)
        decoded = tf.keras.applications.mobilenet_v2.decode_predictions(preds, top=1)[0][0][1]
        category = waste_mapping.get(decoded.lower(), "Unknown")
        return jsonify({"prediction": category})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== Soil Analysis =====
@app.route("/soil-analysis", methods=["POST"])
def soil_analysis():
    data = request.json
    ph = data.get("pH")
    potash = data.get("potashLevel")
    if ph is None or potash is None:
        return jsonify({"error": "Missing input values"}), 400

    try:
        exe = "./soil_analysis" if os.name != "nt" else "soil_analysis.exe"
        # Call the C++ executable with ph and potash
        result = subprocess.check_output([exe], input=f"{ph} {potash}\n", text=True)

        return jsonify({"result": result.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ===== Carbon Footprint =====
# @app.route("/carbon-footprint", methods=["POST"])
# def carbon_footprint():
#     data = request.json
#     electricity = data.get("electricity")
#     water = data.get("water")
#     transport = data.get("transport")
#     if electricity is None or water is None or transport is None:
#         return jsonify({"error": "Missing input values"}), 400

#     try:
#         exe = "./carbon_footprint" if os.name != "nt" else "footprint.exe"
#         result = subprocess.check_output([exe], input=f"{electricity} {water} {transport}\n", text=True)

#         return jsonify({"footprint": result.strip()})
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
@app.route("/carbon-footprint", methods=["POST"])
def carbon_footprint():
    data = request.json
    electricity = data.get("electricity")
    water = data.get("water")
    transport = data.get("transport")

    if electricity is None or water is None or transport is None:
        return jsonify({"error": "Missing input values"}), 400

    try:
        exe = os.path.join(os.getcwd(), "footprint.exe")  # full path
        # Pass input via stdin
        result = subprocess.check_output([exe], input=f"{electricity} {water} {transport}\n", text=True)
        return jsonify({"footprint": result.strip()})
    except Exception as e:
     return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True)
