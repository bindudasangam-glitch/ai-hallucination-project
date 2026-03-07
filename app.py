from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import random

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

history = []

# -----------------------
# DATABASE
# -----------------------

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

# -----------------------
# IMAGE ANSWER
# -----------------------

def image_answer(filename):

    name = filename.lower()

    if "apple" in name:
        return "The uploaded image looks like an apple."

    elif "banana" in name:
        return "The uploaded image looks like a banana."

    elif "fruit" in name:
        return "The uploaded image appears to be a fruit."

    else:
        return f"The uploaded image file is '{filename}'. Image recognition is simulated in this demo."

# -----------------------
# TEXT ANSWER
# -----------------------

def get_ai_answer(question):

    q = question.lower()

    if "java" in q:
        return "Java is a high level object oriented programming language."

    elif "python" in q:
        return "Python is a popular programming language used for AI and data science."

    elif "data structure" in q:
        return "A data structure is a way of organizing data efficiently."

    elif "cricket" in q:
        return "Cricket is a bat and ball sport played between two teams."

    elif "prime minister of india" in q:
        return "The Prime Minister of India is Narendra Modi."

    else:
        return f"This is a demo AI response for the question: {question}"

# -----------------------
# HALLUCINATION SCORE
# -----------------------

def hallucination_score(answer):

    score = 10

    if len(answer) < 50:
        score += 20

    score += random.randint(0,10)

    return min(score,100)

# -----------------------
# LOGIN
# -----------------------

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

        return "Invalid login"

    return render_template("login.html")

# -----------------------
# REGISTER
# -----------------------

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

# -----------------------
# CHAT
# -----------------------

@app.route("/chat", methods=["GET","POST"])
def chat():

    if "user" not in session:
        return redirect("/")

    question = None
    answer = None
    score = None

    if request.method == "POST":

        question = request.form.get("question")

        file = request.files.get("image")

        # IMAGE UPLOAD
        if file and file.filename != "":

            filename = file.filename
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)

            question = f"Image uploaded: {filename}"
            answer = image_answer(filename)

        else:

            answer = get_ai_answer(question)

        score = hallucination_score(answer)

        # STORE HISTORY
        history.append({
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

# -----------------------
# HISTORY OPEN
# -----------------------

@app.route("/history/<int:id>")
def open_history(id):

    if "user" not in session:
        return redirect("/")

    item = history[id]

    return render_template(
        "index.html",
        question=item["question"],
        answer=item["answer"],
        score=item["score"],
        history=history
    )

# -----------------------
# LOGOUT
# -----------------------

@app.route("/logout")
def logout():

    session.pop("user",None)

    return redirect("/")

# -----------------------

if __name__ == "__main__":
    app.run(debug=True)