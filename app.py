from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

# -------------------------
# Upload folder
# -------------------------

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# -------------------------
# History list
# -------------------------

history = []

# -------------------------
# Create database
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
# Demo AI Answer Generator
# -------------------------

def get_ai_answer(question):

    q = question.lower()

    if "java" in q:
        return "Java is a high level object oriented programming language used to build web, mobile and enterprise applications."

    elif "python" in q:
        return "Python is a popular programming language known for its simple syntax and powerful libraries used in AI, data science and web development."

    elif "data structure" in q:
        return "A data structure is a way of organizing and storing data so that it can be accessed and modified efficiently."

    elif "ai" in q or "artificial intelligence" in q:
        return "Artificial Intelligence is a field of computer science that enables machines to simulate human intelligence and perform tasks such as learning and decision making."

    elif "machine learning" in q:
        return "Machine Learning is a subset of Artificial Intelligence that allows computers to learn patterns from data and make predictions."

    elif "hello" in q or "hi" in q:
        return "Hello! I am your AI assistant. Ask me any question."

    else:
        return "This is a demo AI generated answer for the question: " + question

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

    if len(answer) > 250:
        score += 10

    if score == 0:
        score = 10

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
# Chat Page
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

# -------------------------
# History open
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
# Run app
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)