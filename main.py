
from flask import Flask, request, jsonify, render_template, session
from PIL import Image
import numpy as np
import tensorflow as tf
from flask_cors import CORS
import os
import json
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -----------------------------
# App setup
# -----------------------------
app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
CORS(app, supports_credentials=True)

# -----------------------------
# Database setup
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///leaderboard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)
    correct_classifications = db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()

# -----------------------------
# Load AI Model
# -----------------------------
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

RECYCLING_CENTERS = [
    {"name": "Recycling Plant 1", "lat": 23.2335, "lng": 77.4330},
    {"name": "Recycling Plant 2", "lat": 23.2700, "lng": 77.4000},
    {"name": "Nearby Plant", "lat": 23.2000, "lng": 77.5000}
]

# -----------------------------
# User Storage
# -----------------------------
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# -----------------------------
# Helpers
# -----------------------------
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "username" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated

def predict_image(image: Image.Image) -> str:
    img_resized = image.resize(target_size)
    img_array = tf.keras.preprocessing.image.img_to_array(img_resized)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    preds = model.predict(img_array)
    predicted_class = np.argmax(preds, axis=1)[0]
    return idx_to_class.get(predicted_class, "unknown")

def get_waste_info(label):
    return waste_mapping.get(label.lower(), {"type": "Unknown Waste", "recycling_process": "Check locally."})

def calculate_points(waste_type):
    mapping = {
        "Plastic Waste": 10,
        "Paper Waste": 10,
        "Glass Waste": 10,
        "Metal Waste": 10,
        "E-Waste": 20,
        "Other Waste": 5,
        "Unknown Waste": 0
    }
    return mapping.get(waste_type, 5)

def update_user_score(username, points_earned):
    user = Leaderboard.query.filter_by(username=username).first()
    if not user:
        user = Leaderboard(username=username, points=points_earned, correct_classifications=1)
        db.session.add(user)
    else:
        user.points += points_earned
        user.correct_classifications += 1
    db.session.commit()

# -----------------------------
# Routes
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

# ---- Auth ----
@app.route("/register", methods=["POST"])
def register_user():
    data = request.json or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not username or not email or not password:
        return jsonify({"error": "All fields are required"}), 400

    users = load_users()
    if username in users or any(u.get("email") == email for u in users.values()):
        return jsonify({"error": "Username/email already exists"}), 400

    users[username] = {"email": email, "password": generate_password_hash(password)}
    save_users(users)
    return jsonify({"message": "Registration successful!"}), 201

@app.route("/login", methods=["POST"])
def login_user():
    data = request.json or {}
    identifier = (data.get("username") or data.get("email") or "").strip()
    password = data.get("password") or ""

    users = load_users()
    user = None
    username = None

    # Match username or email
    if identifier in users:
        username = identifier
        user = users[username]
    else:
        for uname, udata in users.items():
            if udata.get("email") == identifier:
                username = uname
                user = udata
                break

    if not user or not check_password_hash(user.get("password", ""), password):
        return jsonify({"error": "Invalid credentials"}), 401

    session["username"] = username
    return jsonify({"message": "Login successful!", "username": username}), 200


@app.route("/reset-password", methods=["POST"])
def reset_password():
    """
    JSON input:
    {
        "email": "user@example.com",
        "newPassword": "newpass123"
    }
    """
    data = request.get_json(force=True)
    email = (data.get("email") or "").strip()
    new_password = data.get("newPassword") or ""

    if not email or not new_password:
        return jsonify({"error": "Email and new password are required"}), 400

    # Reload users fresh
    users = load_users()
    user_found = None

    # Find user by email
    for username, udata in users.items():
        if udata.get("email") == email:
            user_found = username
            break

    if not user_found:
        return jsonify({"error": "Email not found"}), 404

    # Update password hash
    users[user_found]["password"] = generate_password_hash(new_password)

    # Save immediately
    save_users(users)

    return jsonify({"message": f"Password reset successful for {user_found}!"}), 200


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.pop("username", None)
    return jsonify({"message": "Logged out successfully"}), 200

# ---- Prediction ----
@app.route("/predict", methods=["POST"])
@login_required
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    try:
        img = Image.open(request.files["file"].stream).convert("RGB")
        prediction = predict_image(img)
        waste_info = get_waste_info(prediction)

        points = calculate_points(waste_info["type"])
        update_user_score(session["username"], points)

        return jsonify({
            "prediction": prediction,
            "waste_type": waste_info["type"],
            "recycling_process": waste_info["recycling_process"],
            "dustbin": dustbin_guide.get(waste_info["type"], "Unknown Bin")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---- Leaderboard ----
@app.route("/api/leaderboard", methods=["GET"])
def get_leaderboard():
    top_users = Leaderboard.query.order_by(Leaderboard.points.desc()).limit(10).all()
    result = [{"rank": i+1, "username": u.username, "points": u.points, "correct_classifications": u.correct_classifications} 
              for i, u in enumerate(top_users)]
    return jsonify(result)

# ---- Check Auth ----
@app.route("/check-auth", methods=["GET"])
def check_auth():
    username = session.get("username")
    if username:
        users = load_users()
        user = users.get(username, {})
        return jsonify({
            "loggedIn": True,
            "username": username,
            "email": user.get("email")
        })
    return jsonify({"loggedIn": False})

# ---- Recycling Centers ----
@app.route('/map')
def map_view():
    return render_template("map.html")

@app.route('/api/recycling-centers')
def recycling_centers():
    return jsonify(RECYCLING_CENTERS)

# ---- Nearby Recycling ----
@app.route("/nearby")
@login_required
def nearby():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    type_filter = request.args.get("type", "general").lower()
    if not lat or not lon:
        return jsonify({"error": "Missing latitude/longitude"}), 400
    try:
        import requests
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
                {"name": "Eco Recycling Hub", "lat": float(lat)+0.01, "lon": float(lon)+0.01, "type": "plastic"},
                {"name": "Green E-Waste Solutions", "lat": float(lat)-0.01, "lon": float(lon)-0.01, "type": "e-waste"}
            ]
        return jsonify({"centers": centers})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ---- Contact Us ----

# # Configure your email credentials
SMTP_SERVER = "smtp.gmail.com"   # or your SMTP server
SMTP_PORT = 587
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")  # sender email
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")  # sender password or app password

@app.route("/contact", methods=["POST"])
def contact_us():
    data = request.get_json(force=True)
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()

    if not name or not email or not message:
        return jsonify({"error": "All fields are required"}), 400

    # Save message to file (optional)
    CONTACT_FILE = "contacts.json"
    if os.path.exists(CONTACT_FILE):
        with open(CONTACT_FILE, "r") as f:
            contacts = json.load(f)
    else:
        contacts = []

    contacts.append({"name": name, "email": email, "message": message})
    with open(CONTACT_FILE, "w") as f:
        json.dump(contacts, f, indent=2)

    # Send email to support
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = "aware.sup@gmail.com"
        msg['Subject'] = f"Contact Form Message from {name}"

        body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500

    return jsonify({"message": "Your message has been sent! Thank you."}), 200

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    if not os.path.exists(USERS_FILE):
        save_users({})
    app.run(host="0.0.0.0", port=5000, debug=True)

