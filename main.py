

from flask import Flask, request, jsonify, render_template, session
from PIL import Image
import numpy as np
import tensorflow as tf
from flask_cors import CORS
import os
import json
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__, template_folder="templates")
# IMPORTANT: change this in production (use env var)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
# If you need to allow cross-origin cookies from another origin, set supports_credentials=True
CORS(app, supports_credentials=True)

# ============================
# Load Model & Labels (your original code)
# ============================
model = tf.keras.models.load_model("trashnet_model.h5")
target_size = (224, 224)

with open("labels.json", "r") as f:
    class_indices = json.load(f)

idx_to_class = {v: k for k, v in class_indices.items()}

waste_mapping = {
    "cardboard": {"type": "Paper Waste", "recycling_process": "Recycle in paper bin."},
    "glass": {"type": "Glass Waste", "recycling_process": "Recycle in glass bin."},
    "metal": {"type": "Metal Waste", "recycling_process": "Recycle in metal bin."},
    "paper": {"type": "Paper Waste", "recycling_process": "Recycle in paper bin."},
    "plastic": {"type": "Plastic Waste", "recycling_process": "Recycle in plastic bin."},
    "trash": {"type": "Other Waste", "recycling_process": "Dispose responsibly."},
    "battery": {"type": "E-Waste", "recycling_process": "Take to e-waste center."}
}

dustbin_guide = {
    "Plastic Waste": "Blue Bin",
    "Paper Waste": "Green Bin",
    "Metal Waste": "Yellow Bin",
    "Organic Waste": "Brown Bin",
    "Glass Waste": "Blue Bin",
    "E-Waste": "Red Bin",
    "Other Waste": "Black Bin",
    "Unknown Waste": "Check locally"
}

# ============================
# Prediction Function
# ============================
def predict_image(image: Image.Image) -> str:
    img_resized = image.resize(target_size)
    img_array = tf.keras.preprocessing.image.img_to_array(img_resized)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0
    preds = model.predict(img_array)
    predicted_class = np.argmax(preds, axis=1)[0]
    return idx_to_class.get(predicted_class, "unknown")

def get_waste_info(label):
    label = label.lower()
    return waste_mapping.get(label, {"type": "Unknown Waste", "recycling_process": "Check locally."})

# ============================
# Simple User storage (file-based)
# ============================
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# Decorator to protect routes
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated

# ============================
# Routes
# ============================
@app.route("/")
def home():
    return render_template("index.html")

# Auth endpoints
@app.route("/register", methods=["POST"])
def register_user():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not username or not email or not password:
        return jsonify({"error": "All fields (username, email, password) are required"}), 400

    users = load_users()
    if username in users:
        return jsonify({"error": "Username already exists"}), 400

    # Simple uniqueness check for email
    if any(u.get("email") == email for u in users.values()):
        return jsonify({"error": "Email already registered"}), 400

    users[username] = {
        "email": email,
        "password": generate_password_hash(password)
    }
    save_users(users)
    return jsonify({"message": "Registration successful!"}), 201

@app.route("/login", methods=["POST"])
def login_user():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    users = load_users()
    user = users.get(username)
    if not user or not check_password_hash(user.get("password", ""), password):
        return jsonify({"error": "Invalid credentials"}), 401

    # Put username into session (Flask will send a secure cookie)
    session["username"] = username
    return jsonify({"message": "Login successful!", "username": username}), 200

@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("username", None)
    return jsonify({"message": "Logged out"}), 200

@app.route("/me")
def get_current_user():
    username = session.get("username")
    if not username:
        return jsonify({"username": None}), 200
    # Optionally return email or more info (avoid sensitive data)
    users = load_users()
    user = users.get(username, {})
    return jsonify({"username": username, "email": user.get("email")}), 200

# ============================
# Prediction (Protected)
# ============================
@app.route("/predict", methods=["POST"])
@login_required
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    try:
        file = request.files["file"]
        img = Image.open(file.stream).convert("RGB")
        prediction = predict_image(img)
        waste_info = get_waste_info(prediction)
        return jsonify({
            "prediction": prediction,
            "waste_type": waste_info["type"],
            "recycling_process": waste_info["recycling_process"],
            "dustbin": dustbin_guide.get(waste_info["type"], "Unknown Bin")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================
# Nearby Recycling Centers (Protected)
# ============================
@app.route("/nearby")
@login_required
def nearby():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    type_filter = request.args.get("type", "general").lower()
    if not lat or not lon:
        return jsonify({"error": "Missing latitude/longitude"}), 400

    try:
        query = f"""
        [out:json];
        node(around:20000,{lat},{lon})[amenity=recycling];
        out;
        """
        response = requests.get("http://overpass-api.de/api/interpreter", params={"data": query}, timeout=15)
        data = response.json()

        centers = []
        for el in data.get("elements", []):
            center_type = el.get("tags", {}).get("recycling_type", "general").lower()
            if type_filter == "general" or type_filter in center_type:
                centers.append({
                    "name": el.get("tags", {}).get("name", "Recycling Center"),
                    "lat": el["lat"],
                    "lon": el["lon"],
                    "type": center_type
                })

        if not centers:
            centers = [
                {"name": "Eco Recycling Hub", "lat": float(lat) + 0.01, "lon": float(lon) + 0.01, "type": "plastic"},
                {"name": "Green E-Waste Solutions", "lat": float(lat) - 0.01, "lon": float(lon) - 0.01, "type": "e-waste"}
            ]

        return jsonify({"centers": centers}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================
if __name__ == "__main__":
    # make sure users.json exists (optional)
    if not os.path.exists(USERS_FILE):
        save_users({})
    app.run(host="0.0.0.0", port=5000, debug=True)
