# 🌀 Text Morph – Advanced Text Summarization & Readability Analysis

## 📌 Overview
**Text Morph** is a full-stack application built with **FastAPI (backend)** and **Streamlit (frontend)** that allows users to:
- Register/Login securely
- Manage their profile (name, age, language preferences, bio, and profile picture)
- Upload or paste text documents
- Perform **readability analysis** using Flesch-Kincaid, Gunning Fog, and SMOG Index
- Visualize **complexity distribution** (Beginner, Intermediate, Advanced) using interactive bar charts

This project is useful for students, educators, and researchers who want to quickly check the readability and complexity of text.

---

## 🚀 Features
- 🔑 **User Authentication** (Register/Login with validation)
- 👤 **Profile Management** (update, delete, profile picture upload)
- 📂 **Text Input** (upload `.txt` file or paste text)
- 📊 **Readability Scores** (Flesch-Kincaid, Gunning Fog, SMOG Index)
- 📉 **Complexity Distribution** (bar chart visualization)
- 🔒 **Secure JWT Authentication** for backend APIs

---

## 🛠️ Tech Stack
- **Frontend**: Streamlit  
- **Backend**: FastAPI, Uvicorn  
- **Database**: SQLite (via SQLAlchemy)  
- **Text Analysis**: Textstat  
- **Visualization**: Matplotlib  

---

## 📂 Project Structure
text-morph/
│── backend/
│ ├── main.py
│ ├── database.py
│ ├── create_db.py
│ ├── models.py
│ ├── schemas.py
│ ├── auth.py
│ ├── crud.py
│── frontend/
│ ├── app.py
│── requirements.txt
│── README.md

yaml
Copy code

---

## ⚙️ Installation

### 1️⃣ Clone the repo
```bash
git clone https://github.com/your-username/text-morph.git
cd text-morph

### 2️⃣ Create a virtual environment
python -m venv venv
source venv/bin/activate   # for Linux/Mac
venv\Scripts\activate      # for Windows

### 3️⃣ Install dependencies
pip install -r requirements.txt

### ▶️ Running the Project
Start Backend (FastAPI)
cd backend
uvicorn main:app --reload


Backend will run at: http://127.0.0.1:8000

Start Frontend (Streamlit)
cd frontend
streamlit run app.py


Frontend will run at: http://localhost:8501


