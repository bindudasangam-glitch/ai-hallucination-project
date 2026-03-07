from flask import Flask, render_template, request, redirect, session
import os
import random
import re

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

history = []

# -----------------------------
# IMAGE ANSWER
# -----------------------------

def image_answer(filename):

    return f"The uploaded image '{filename}' was successfully received. Image recognition is simulated in this demo."

# -----------------------------
# HALLUCINATION SCORE
# -----------------------------

def hallucination_score():

    score = random.randint(5,80)

    if score < 30:
        level = "low"

    elif score < 60:
        level = "medium"

    else:
        level = "high"

    return score, level

# -----------------------------
# AI ANSWER LOGIC
# -----------------------------

def get_ai_answer(question):

    q = question.lower()

    # -------------------------
    # EQUATION CHECK
    # -------------------------

    equation = re.search(r'(\d+[\+\-\*/]\d+)\s*=\s*(\d+)', q)

    if equation:

        left = equation.group(1)
        right = int(equation.group(2))

        correct = eval(left)

        if correct == right:
            return f"Yes, the equation {left} = {right} is correct."

        else:
            return f"No, the equation is incorrect. The correct answer is {correct}."

    # -------------------------
    # SIMPLE MATH
    # -------------------------

    math = re.search(r'(\d+[\+\-\*/]\d+)', q)

    if math:

        result = eval(math.group(1))

        return f"The correct answer is {result}."

    # -------------------------
    # PROGRAMMING
    # -------------------------

    if "java" in q:
        return "Java is a high level object oriented programming language used to build applications."

    if "python" in q:
        return "Python is widely used for AI, machine learning and data science."

    # -------------------------
    # EDUCATION
    # -------------------------

    if "data structure" in q:
        return "A data structure is a way of organizing and storing data efficiently."

    if "algorithm" in q:
        return "An algorithm is a step by step procedure used to solve problems."

    # -------------------------
    # SPORTS
    # -------------------------

    if "cricket" in q:
        return "Cricket is a bat and ball sport played between two teams of eleven players."

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
    # GENERAL DEFAULT
    # -------------------------

    return f"This system generated an AI response related to: {question}"

# -----------------------------
# LOGIN
# -----------------------------

@app.route("/", methods=["GET","POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":

            session["user"] = username
            return redirect("/chat")

        return "Invalid login"

    return render_template("login.html")

# -----------------------------
# CHAT
# -----------------------------

@app.route("/chat", methods=["GET","POST"])
def chat():

    if "user" not in session:
        return redirect("/")

    question=None
    answer=None
    score=None
    level=None

    if request.method == "POST":

        question=request.form.get("question")
        file=request.files.get("image")

        if file and file.filename!="":

            filename=file.filename
            path=os.path.join(UPLOAD_FOLDER,filename)
            file.save(path)

            question=f"Image uploaded: {filename}"
            answer=image_answer(filename)

        else:

            answer=get_ai_answer(question)

        score, level = hallucination_score()

        history.append({
            "question":question,
            "answer":answer,
            "score":score,
            "level":level
        })

    return render_template(
        "index.html",
        question=question,
        answer=answer,
        score=score,
        level=level,
        history=history
    )

# -----------------------------
# HISTORY
# -----------------------------

@app.route("/history/<int:id>")
def open_history(id):

    if id>=len(history):
        return redirect("/chat")

    item=history[id]

    return render_template(
        "index.html",
        question=item["question"],
        answer=item["answer"],
        score=item["score"],
        level=item["level"],
        history=history
    )

# -----------------------------
# LOGOUT
# -----------------------------

@app.route("/logout")
def logout():

    session.pop("user",None)
    return redirect("/")

if __name__=="__main__":
    app.run(debug=True)