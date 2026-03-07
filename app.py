from flask import Flask, render_template, request, redirect, session
import os
import random
import ast
import operator as op

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

history = []

# -------------------------
# SAFE MATH EVALUATION
# -------------------------

operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv
}

def eval_expr(expr):

    try:
        node = ast.parse(expr, mode='eval').body

        if isinstance(node, ast.BinOp):
            return operators[type(node.op)](
                eval_expr_node(node.left),
                eval_expr_node(node.right)
            )
    except:
        return None

def eval_expr_node(node):

    if isinstance(node, ast.Num):
        return node.n

    if isinstance(node, ast.BinOp):
        return operators[type(node.op)](
            eval_expr_node(node.left),
            eval_expr_node(node.right)
        )

# -------------------------
# IMAGE ANSWER
# -------------------------

def image_answer(filename):

    return f"The uploaded image '{filename}' was successfully received. Image recognition is simulated in this demo system."

# -------------------------
# TEXT AI ANSWER
# -------------------------

def get_ai_answer(question):

    q = question.lower().strip()

    # try math calculation
    try:
        cleaned = q.replace(" ","")

        if any(op in cleaned for op in ["+","-","*","/"]):
            result = eval(cleaned)
            return f"The correct answer is {result}."
    except:
        pass

    # programming
    if "python" in q:
        return "Python is a popular programming language widely used for AI, data science, and web development."

    if "java" in q:
        return "Java is an object oriented programming language commonly used for enterprise and mobile applications."

    # education
    if "data structure" in q:
        return "A data structure is a method of organizing data efficiently for processing."

    if "algorithm" in q:
        return "An algorithm is a step by step procedure used to solve computational problems."

    # sports
    if "cricket" in q:
        return "Cricket is a bat and ball sport played between two teams of eleven players."

    if "football" in q:
        return "Football is a team sport played with a spherical ball between two teams."

    # politics
    if "prime minister of india" in q:
        return "The Prime Minister of India is Narendra Modi."

    if "president of india" in q:
        return "The President of India is Droupadi Murmu."

    # general knowledge
    if "capital of india" in q:
        return "The capital of India is New Delhi."

    if "who invented computer" in q:
        return "Charles Babbage is considered the father of the computer."

    # default answer
    return f"The question '{question}' relates to general knowledge. This system provides a simulated AI generated response."

# -------------------------
# HALLUCINATION SCORE
# -------------------------

def hallucination_score(answer):

    score = random.randint(5,60)

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

# -------------------------
# HISTORY
# -------------------------

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

# -------------------------
# LOGOUT
# -------------------------

@app.route("/logout")
def logout():

    session.pop("user",None)

    return redirect("/")

# -------------------------

if __name__=="__main__":
    app.run(debug=True)