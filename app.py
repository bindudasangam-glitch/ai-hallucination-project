from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import random

app = Flask(__name__)
app.secret_key = "secret123"

# -------------------------
# Upload folder
# -------------------------

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------------------------
# History storage
# -------------------------

history = []

# -------------------------
# Database setup
# -------------------------

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

# -------------------------
# AI Answer Generator
# -------------------------

def get_ai_answer(question):

    q = question.lower()

    # SPORTS
    if "cricket" in q:
        return "Cricket is a popular bat and ball sport played between two teams of eleven players each."

    elif "football" in q:
        return "Football is a team sport played with a spherical ball between two teams of eleven players."

    # POLITICS
    elif "prime minister of india" in q:
        return "The Prime Minister of India is Narendra Modi."

    elif "president of india" in q:
        return "The President of India is Droupadi Murmu."

    # EDUCATION
    elif "data structure" in q:
        return "A data structure is a way of organizing and storing data efficiently for processing and retrieval."

    elif "algorithm" in q:
        return "An algorithm is a step by step procedure used to solve a problem or perform a task."

    # PROGRAMMING
    elif "java" in q:
        return "Java is a high level object oriented programming language used to develop web and enterprise applications."

    elif "python" in q:
        return "Python is a powerful programming language widely used in AI, data science, automation and web development."

    # AI
    elif "artificial intelligence" in q or "ai" in q:
        return "Artificial Intelligence is a branch of computer science that enables machines to perform tasks that normally require human intelligence."

    elif "machine learning" in q:
        return "Machine Learning is a subset of Artificial Intelligence that allows systems to learn patterns from data and make predictions."

    # GENERAL KNOWLEDGE
    elif "capital of india" in q:
        return "The capital of India is New Delhi."

    elif "who invented computer" in q:
        return "Charles Babbage is considered the father of the computer."

    # DEFAULT
    else:
        return f"Based on general knowledge, the answer related to '{question}' involves concepts that require further detailed explanation."

# -------------------------
# Hallucination Score
# -------------------------

def hallucination_score(answer):

    keywords = [
        "maybe","might","possibly",
        "uncertain","not sure",
        "likely","probably","guess"
    ]

    score = 0

    for k in keywords:
        if k in answer.lower():
            score += 20

    # Answer length impact
    if len(answer) < 50:
        score += 40
    elif len(answer) < 120:
        score += 25
    else:
        score += 10

    # Random factor
    score += random.randint(0,15)

    if score > 100:
        score = 100

    return score

# -------------------------
# Login
# -------------------------

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

# -------------------------
# Register
# -------------------------

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

# -------------------------
# Chat
# -------------------------

@app.route("/chat", methods=["GET","POST"])
def chat():

    if "user" not in session:
        return redirect("/")

    question = None
    answer = None
    score = None

    if request.method == "POST":

        question = request.form["question"]

        file = request.files.get("image")

        if file and file.filename != "":
            path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(path)

        answer = get_ai_answer(question)

        score = hallucination_score(answer)

        history.insert(0,{
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

# -------------------------
# History
# -------------------------

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

# -------------------------
# Logout
# -------------------------

@app.route("/logout")
def logout():

    session.pop("user",None)

    return redirect("/")

# -------------------------
# Run
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)