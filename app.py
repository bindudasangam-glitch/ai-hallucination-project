from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import random
import re

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

history = []

# -------------------------
# DATABASE
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
# IMAGE ANSWER
# -------------------------

def image_answer(filename):

    name = filename.lower()

    if "apple" in name:
        return "The uploaded image appears to be an apple."

    if "banana" in name:
        return "The uploaded image appears to be a banana."

    if "fruit" in name:
        return "The uploaded image seems related to fruits."

    return f"The uploaded image file is '{filename}'. Image recognition is simulated in this demo."

# -------------------------
# TEXT AI ANSWER
# -------------------------

def get_ai_answer(question):

    q = question.lower()

    # -------------------------
    # MATH
    # -------------------------

    try:

        exp = question.replace(" ", "")

        if "=" in exp:

            left, right = exp.split("=")

            result = eval(left)

            if str(result) == right:
                return f"Yes, it is correct. {left} = {result}"

            else:
                return f"No, it is incorrect. The correct answer is {left} = {result}"

        elif any(op in exp for op in ["+","-","*","/"]):

            result = eval(exp)

            return f"The answer is {result}"

    except:
        pass

    # -------------------------
    # PROGRAMMING
    # -------------------------

    if "java" in q:
        return "Java is a high level object oriented programming language."

    if "python" in q:
        return "Python is widely used for AI, automation and data science."

    # -------------------------
    # SPORTS
    # -------------------------

    if "cricket" in q:
        return "Cricket is a bat and ball sport played between two teams."

    if "football" in q:
        return "Football is a team sport played with a spherical ball."

    # -------------------------
    # POLITICS
    # -------------------------

    if "prime minister of india" in q:
        return "The Prime Minister of India is Narendra Modi."

    if "president of india" in q:
        return "The President of India is Droupadi Murmu."

    # -------------------------
    # EDUCATION
    # -------------------------

    if "data structure" in q:
        return "A data structure is a method of organizing and storing data efficiently."

    if "algorithm" in q:
        return "An algorithm is a step-by-step procedure to solve a problem."

    # -------------------------
    # GENERAL
    # -------------------------

    if "capital of india" in q:
        return "The capital of India is New Delhi."

    return f"This system generated a general AI response related to: {question}"

# -------------------------
# HALLUCINATION SCORE
# -------------------------

def hallucination_score(answer):

    score = 10

    if len(answer) < 40:
        score += 30
    elif len(answer) < 100:
        score += 15

    score += random.randint(0,10)

    if score > 100:
        score = 100

    return score

# -------------------------
# LOGIN
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

        return "Invalid login"

    return render_template("login.html")

# -------------------------
# REGISTER
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
# CHAT
# -------------------------

@app.route("/chat", methods=["GET","POST"])
def chat():

    if "user" not in session:
        return redirect("/")

    question = None
    answer = None
    score = None

    if request.method == "POST":

        question = request.form.get("question","")

        file = request.files.get("image")

        if file and file.filename != "":

            filename = file.filename
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)

            question = f"Image uploaded: {filename}"

            answer = image_answer(filename)

        else:

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
# HISTORY
# -------------------------

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

# -------------------------
# LOGOUT
# -------------------------

@app.route("/logout")
def logout():

    session.pop("user",None)
    return redirect("/")

# -------------------------

if __name__ == "__main__":
    app.run(debug=True)