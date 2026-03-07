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
# AI ANSWER
# -------------------------

def get_ai_answer(question, image_name=None):

    q = question.lower()

    # -------------------------
    # IMAGE RESPONSE
    # -------------------------

    if image_name:
        return f"The uploaded image file name is '{image_name}'. Image processing is simulated in this demo system."

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
        return "Java is a high level object oriented programming language used for building applications."

    if "python" in q:
        return "Python is a popular programming language widely used in AI, data science and automation."

    # -------------------------
    # SPORTS
    # -------------------------

    if "cricket" in q:
        return "Cricket is a bat and ball sport played between two teams of eleven players."

    if "football" in q:
        return "Football is a team sport played between two teams."

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
        return "A data structure is a way of organizing and storing data efficiently."

    if "algorithm" in q:
        return "An algorithm is a step-by-step procedure used to solve a problem."

    # -------------------------
    # GENERAL KNOWLEDGE
    # -------------------------

    if "capital of india" in q:
        return "The capital of India is New Delhi."

    if "who invented computer" in q:
        return "Charles Babbage is known as the father of the computer."

    # -------------------------
    # DEFAULT
    # -------------------------

    return f"This system generated a general response related to: {question}"

# -------------------------
# HALLUCINATION SCORE
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

    if len(answer) < 40:
        score += 35
    elif len(answer) < 100:
        score += 20
    else:
        score += 10

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

        image_name = None

        if file and file.filename != "":
            image_name = file.filename
            path = os.path.join(UPLOAD_FOLDER, image_name)
            file.save(path)

        answer = get_ai_answer(question, image_name)

        score = hallucination_score(answer)

        history.insert(0,{
            "id": len(history),
            "question": question if question else image_name,
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
# LOGOUT
# -------------------------

@app.route("/logout")
def logout():

    session.pop("user",None)

    return redirect("/")

# -------------------------

if __name__ == "__main__":
    app.run(debug=True)