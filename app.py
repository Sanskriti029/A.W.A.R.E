from flask import Flask, request, jsonify, render_template
from PIL import Image
import numpy as np
import tensorflow as tf
import subprocess
import os

app = Flask(__name__)

# Pre-trained MobileNetV2
base_model = tf.keras.applications.MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
target_size = (224, 224)

# Waste categories (demo mapping based on color heuristics or ImageNet labels)
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

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files["file"]
    try:
        img = Image.open(file).convert("RGB")
        img = img.resize(target_size)
        x = np.array(img) / 255.0
        x = np.expand_dims(x, axis=0)

        # Extract features
        features = base_model.predict(x)

        # For demo: use ImageNet class predictions for mapping
        # Use decode_predictions to map to ImageNet labels
        preds = tf.keras.applications.mobilenet_v2.decode_predictions(
            tf.keras.applications.mobilenet_v2.preprocess_input(x), top=1
        )[0][0][1]

        # Map to our waste categories
        category = waste_mapping.get(preds.lower(), "Unknown")
        return jsonify({"prediction": category})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Soil Analysis via C++ (unchanged)
@app.route("/soil-analysis", methods=["POST"])
def soil_analysis():
    data = request.json
    pH = data.get("pH")
    potash = data.get("potashLevel")
    try:
        exe = "./soil_analysis" if os.name != "nt" else "soil_analysis.exe"
        result = subprocess.check_output([exe, str(pH), str(potash)])
        return jsonify({"result": result.decode("utf-8")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Carbon Footprint via C++ (unchanged)
@app.route("/carbon-footprint", methods=["POST"])
def carbon_footprint():
    data = request.json
    electricity = data.get("electricity")
    water = data.get("water")
    transport = data.get("transport")
    try:
        exe = "./carbon_footprint" if os.name != "nt" else "carbon_footprint.exe"
        result = subprocess.run(['footprint.exe', str(elec), str(water), str(transport)], capture_output=True, text=True)

        return jsonify({"footprint": result.decode("utf-8")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
