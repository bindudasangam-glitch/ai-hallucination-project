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

    name = filename.lower()

    if "apple" in name:
        return "The uploaded image appears to contain an apple."

    elif "banana" in name:
        return "The uploaded image appears to contain a banana."

    elif "fruit" in name:
        return "The uploaded image seems to contain fruits."

    elif "dog" in name:
        return "The uploaded image appears to contain a dog."

    elif "cat" in name:
        return "The uploaded image appears to contain a cat."

    return f"The uploaded image '{filename}' was successfully received. Image recognition is simulated in this demo."

# -----------------------------
# AI ANSWER LOGIC
# -----------------------------

def get_ai_answer(question):

    q = question.lower()

    # -------------------------
    # EQUATION CHECK
    # -------------------------

    if "=" in q and any(op in q for op in ["+","-","*","/"]):

        try:

            left,right = q.split("=")

            left_val = eval(left.strip())

            right_val = eval(re.findall(r'\d+', right)[0])

            if left_val == right_val:
                return f"Yes, the equation {left_val} = {right_val} is correct."

            else:
                return f"No, the equation is incorrect. The correct answer is {left_val}."

        except:
            pass


    # -------------------------
    # SIMPLE MATH
    # -------------------------

    try:

        expr = re.findall(r'[0-9+\-*/]+', q)

        if expr:

            result = eval(expr[0])

            return f"The correct answer is {result}."

    except:
        pass


    # -------------------------
    # PROGRAMMING
    # -------------------------

    if "java" in q:
        return "Java is a high level object oriented programming language used to build enterprise applications."

    if "python" in q:
        return "Python is a popular programming language widely used in AI, data science and automation."

    # -------------------------
    # EDUCATION
    # -------------------------

    if "data structure" in q:
        return "A data structure is a way of organizing and storing data efficiently."

    if "algorithm" in q:
        return "An algorithm is a step by step procedure used to solve computational problems."

    # -------------------------
    # SPORTS
    # -------------------------

    if "cricket" in q:
        return "Cricket is a bat and ball sport played between two teams of eleven players."

    if "football" in q:
        return "Football is a team sport played between two teams using a spherical ball."

    # -------------------------
    # POLITICS
    # -------------------------

    if "prime minister of india" in q:
        return "The Prime Minister of India is Narendra Modi."

    if "president of india" in q:
        return "The President of India is Droupadi Murmu."

    # -------------------------
    # GENERAL KNOWLEDGE
    # -------------------------

    if "capital of india" in q:
        return "The capital of India is New Delhi."

    if "who invented computer" in q:
        return "Charles Babbage is considered the father of the computer."

    return f"This system generated an AI response related to: {question}"

# -----------------------------
# HALLUCINATION SCORE
# -----------------------------

def hallucination_score(answer):

    score = random.randint(5,60)

    return score

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

        score=hallucination_score(answer)

        history.append({
            "question":question,
            "answer":answer,
            "score":score
        })

    return render_template(
        "index.html",
        question=question,
        answer=answer,
        score=score,
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
        history=history
    )

# -----------------------------
# LOGOUT
# -----------------------------

@app.route("/logout")
def logout():

    session.pop("user",None)
    return redirect("/")

# -----------------------------

if __name__=="__main__":
    app.run(debug=True)