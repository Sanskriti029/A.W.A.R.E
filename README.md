# A.W.A.R.E

## Artificial Waste and Recyling Engine 🌱

**A.W.A.R.E** is an AI-powered waste management and awareness web application designed to promote responsible waste disposal and recycling.
It allows users to classify waste using a trained deep learning model, view recycling guidance, track leaderboard scores, and locate nearby recycling centers using an interactive map.

---

## 🚀 Features

* **🗑️ AI Waste Classification** – Upload an image of waste and get its category using a trained CNN model

* **♻️ Recycling Guide** – Shows correct dustbin color and recycling process

* **🏆 Leaderboard System** – Users earn points for correct classifications

* **👤 User Authentication** – Register, login, logout, and reset password

* **🌍 Recycling Centers Map**– Interactive map using Leaflet

* **🔔 Notifications** – Eco-facts and activity alerts

* **🌐 Community Section** – Share sustainability tips

* **📊 Dustbin Information**– Helps in proper waste segregation

---

## 🛠️ Tech Stack

🛠️ Tech Stack

*Frontend:*

*  HTML, CSS, JavaScript

_Backend:_

*  Flask (Python)

_AI / ML:_

*   TensorFlow (CNN model)

* Trained using Kaggle dataset

_Database & Storage:_

*  SQLite (Leaderboard)

*  JSON (User data & labels)

_Map:_

*  Leaflet (OpenStreetMap)

## 🧩 Folder Structure

```text
A.W.A.R.E/
│
├── templates/
│   └── index.html
├── static/
│   └── images/
├── train_model.py
├── main.py
├── labels.json
├── users.json
├── trashnet_model.h5
├── requirements.txt
└── README.md
````

## 📦 Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Sanskriti029/A.W.A.R.E.git

   ```

2. Navigate to the project folder:

   ```bash
   cd A.W.A.R.E
   ```

3. Create and activate a virtual environment (recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

5. Start the Flask development server:

   ```bash
   python main.py
   ```

---

### 🧠Model Training (Optional – if you want to retrain)

This project uses a custom-trained CNN model.

_Dataset_

Download a waste classification dataset from Kaggle
(example: TrashNet or Garbage Classification Dataset)

*  Place the dataset in this structure:

```bash
dataset/
├── train/
└── test/
```

**Train the model**

```bash
python train_model.py
```
This will generate:

* trashnet_model.h5

* labels.json

**▶️ Run the Application**
```bash
python main.py
```

Then open in your browser:
```
http://127.0.0.1:5000/
```

**🗺️ Map Integration**

The project uses Leaflet (OpenStreetMap) for recycling center locations.
✅ No API key is required.


## 📸 How It Works

1. User uploads a waste image

2. AI model predicts waste type

3. App displays:

 *  Waste category

 * Recycling process

* Dustbin color

4. User earns points

5. Leaderboard updates automatically

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch (`feature/your-feature-name`)
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 📬 Contact

For questions or suggestions:

- **Project Name:** A.W.A.R.E -Artifiial Waste and Recycling Engine
- **GitHub:** [https://github.com/Sanskriti029](https://github.com/Sanskriti029)

---

> _Together, let’s build a cleaner and more sustainable future with Aware._ 🌿

