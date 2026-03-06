from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import requests

app = Flask(__name__)
app.secret_key = "secret123"

# -----------------------------
# Upload folder
# -----------------------------

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -----------------------------
# History storage
# -----------------------------

history = []

# -----------------------------
# Database create
# -----------------------------

def init_db():

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# Hallucination Score
# -----------------------------

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

    if score == 0:
        score = 5

    if score > 100:
        score = 100

    return score

# -----------------------------
# AI Answer (Ollama + fallback)
# -----------------------------

def get_ai_answer(question):

    try:

        url = "http://localhost:11434/api/generate"

        data = {
            "model": "llama3",
            "prompt": question,
            "stream": False
        }

        response = requests.post(url, json=data)

        return response.json()["response"]

    except:

        return "AI model not available on server. This is a demo response generated without the local model."

# -----------------------------
# Login page
# -----------------------------

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        )

        user = c.fetchone()

        conn.close()

        if user:
            session["user"] = username
            return redirect("/chat")

        else:
            return "Invalid login"

    return render_template("login.html")

# -----------------------------
# Register
# -----------------------------

@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        c = conn.cursor()

        c.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username,password)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

# -----------------------------
# Chat page
# -----------------------------

@app.route("/chat", methods=["GET","POST"])
def chat():

    if "user" not in session:
        return redirect("/")

    question = None
    answer = None
    score = None

    if request.method == "POST":

        question = request.form["question"]

        # image upload
        file = request.files.get("image")

        if file and file.filename != "":
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)

        answer = get_ai_answer(question)

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

# -----------------------------
# History open
# -----------------------------

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

# -----------------------------
# Logout
# -----------------------------

@app.route("/logout")
def logout():

    session.pop("user",None)

    return redirect("/")

# -----------------------------
# Run
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)