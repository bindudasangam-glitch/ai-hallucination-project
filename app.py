from flask import Flask, render_template, request, redirect, session
import requests
import os
import sqlite3
import base64

app = Flask(__name__)
app.secret_key = "secret123"

# -------------------------------
# Create uploads folder
# -------------------------------

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------------------------------
# Database path (important for Render)
# -------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "users.db")

# -------------------------------
# Ollama API
# -------------------------------

OLLAMA_URL = "http://localhost:11434/api/generate"
TEXT_MODEL = "llama3"
IMAGE_MODEL = "llava"

history = []

# -------------------------------
# Hallucination score
# -------------------------------

def hallucination_score(answer):

    keywords = [
        "maybe","might","possibly","uncertain",
        "not sure","likely","probably","guess"
    ]

    score = 0

    for k in keywords:
        if k in answer.lower():
            score += 15

    if len(answer) > 300:
        score += 5

    if score > 100:
        score = 100

    return score


# -------------------------------
# LOGIN
# -------------------------------

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email,password)
        )

        user = c.fetchone()
        conn.close()

        if user:
            session["user"] = email
            return redirect("/chat")

        else:
            return "Invalid login"

    return render_template("login.html")


# -------------------------------
# REGISTER
# -------------------------------

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        conn = sqlite3.connect(db_path)
        c = conn.cursor()

        try:

            c.execute(
                "INSERT INTO users(email,password) VALUES(?,?)",
                (email,password)
            )

            conn.commit()
            conn.close()

            return redirect("/")

        except:

            conn.close()
            return "User already exists"

    return render_template("register.html")


# -------------------------------
# CHAT
# -------------------------------

@app.route("/chat", methods=["GET","POST"])
def chat():

    if "user" not in session:
        return redirect("/")

    question = ""
    answer = ""
    score = 0

    if request.method == "POST":

        question = request.form.get("question")
        image = request.files.get("image")

        # ---------------------------
        # IMAGE QUESTION
        # ---------------------------

        if image and image.filename != "":

            filepath = os.path.join(UPLOAD_FOLDER, image.filename)
            image.save(filepath)

            with open(filepath, "rb") as img_file:
                image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

            prompt = "Explain what is in this image."

            try:

                r = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": IMAGE_MODEL,
                        "prompt": prompt,
                        "images": [image_base64],
                        "stream": False
                    }
                )

                result = r.json()
                answer = result.get("response","Image AI failed")

            except:
                answer = "Error connecting to AI model"

        # ---------------------------
        # TEXT QUESTION
        # ---------------------------

        elif question:

            prompt = f"""
You are an intelligent AI assistant.
Answer clearly and correctly.

Question: {question}
Answer:
"""

            try:

                r = requests.post(
                    OLLAMA_URL,
                    json={
                        "model": TEXT_MODEL,
                        "prompt": prompt,
                        "stream": False
                    }
                )

                result = r.json()
                answer = result.get("response","AI failed")

            except:
                answer = "Error connecting to AI model"

        # ---------------------------
        # Hallucination score
        # ---------------------------

        score = hallucination_score(answer)

        history.append({
            "id": len(history),
            "question": question,
            "answer": answer,
            "score": score
        })

    return render_template(
        "index.html",
        question=question,
        answer=answer,
        score=score,
        history=history
    )


# -------------------------------
# HISTORY OPEN
# -------------------------------

@app.route("/history/<int:id>")
def open_history(id):

    if "user" not in session:
        return redirect("/")

    if id >= len(history):
        return redirect("/chat")

    item = history[id]

    return render_template(
        "index.html",
        question=item["question"],
        answer=item["answer"],
        score=item["score"],
        history=history
    )


# -------------------------------
# LOGOUT
# -------------------------------

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")


# -------------------------------
# RUN
# -------------------------------

if __name__ == "__main__":
    app.run(debug=True)