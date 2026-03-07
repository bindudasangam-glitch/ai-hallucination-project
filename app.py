from flask import Flask, render_template, request, redirect, session
import random
import os

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

history = []


# -------------------------
# IMAGE ANSWER
# -------------------------

def image_answer(filename):

    name = filename.lower()

    if "apple" in name:
        return "The uploaded image appears to contain an apple."

    elif "banana" in name:
        return "The uploaded image appears to contain a banana."

    elif "fruit" in name:
        return "The uploaded image seems related to fruits."

    elif "dog" in name:
        return "The uploaded image appears to contain a dog."

    elif "cat" in name:
        return "The uploaded image appears to contain a cat."

    else:
        return f"The uploaded image '{filename}' was received. Image recognition is simulated in this demo."


# -------------------------
# TEXT AI ANSWER
# -------------------------

def get_ai_answer(question):

    q = question.lower()

    # ------------------
    # MATH
    # ------------------

    try:
        if any(op in q for op in ["+","-","*","/"]):
            result = eval(q)
            return f"The correct answer is {result}."
    except:
        pass

    # ------------------
    # PROGRAMMING
    # ------------------

    if "java" in q:
        return "Java is a high level object oriented programming language used to build enterprise and web applications."

    if "python" in q:
        return "Python is a powerful programming language widely used in AI, data science and automation."

    # ------------------
    # EDUCATION
    # ------------------

    if "data structure" in q:
        return "A data structure is a way of organizing and storing data so that it can be accessed efficiently."

    if "algorithm" in q:
        return "An algorithm is a step by step procedure used to solve a computational problem."

    # ------------------
    # SPORTS
    # ------------------

    if "cricket" in q:
        return "Cricket is a bat and ball sport played between two teams of eleven players."

    if "football" in q:
        return "Football is a team sport played between two teams using a spherical ball."

    # ------------------
    # POLITICS
    # ------------------

    if "prime minister of india" in q:
        return "The Prime Minister of India is Narendra Modi."

    if "president of india" in q:
        return "The President of India is Droupadi Murmu."

    # ------------------
    # GENERAL KNOWLEDGE
    # ------------------

    if "capital of india" in q:
        return "The capital of India is New Delhi."

    if "who invented computer" in q:
        return "Charles Babbage is considered the father of the computer."

    # ------------------
    # DEFAULT
    # ------------------

    return f"This system generated an AI response related to: {question}"


# -------------------------
# HALLUCINATION SCORE
# -------------------------

def hallucination_score(answer):

    score = random.randint(5,50)

    return score


# -------------------------
# LOGIN
# -------------------------

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

        question = request.form.get("question")
        file = request.files.get("image")

        # IMAGE
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


if __name__ == "__main__":
    app.run(debug=True)