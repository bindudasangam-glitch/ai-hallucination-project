from flask import Flask, render_template, request, redirect
import os
import random
import re

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

history = []

# ---------------- AI ANSWER FUNCTION ---------------- #

def get_ai_answer(question):

    q = question.lower()

    # --------- MATH DETECTION ---------

    match = re.search(r'(\d+)\s*([\+\-\*\/])\s*(\d+)', q)

    if match:

        a = int(match.group(1))
        op = match.group(2)
        b = int(match.group(3))

        if op == "+":
            correct = a + b
        elif op == "-":
            correct = a - b
        elif op == "*":
            correct = a * b
        elif op == "/":
            correct = a / b

        if str(correct) in q:
            return f"Yes, the equation is correct. {a} {op} {b} = {correct}.", random.randint(5,20)
        else:
            return f"No, the equation is incorrect. The correct answer is {correct}.", random.randint(60,80)


    # --------- INDIA NATIONAL SYMBOLS ---------

    if "national" in q and "animal" in q and "india" in q:
        return "The national animal of India is the Bengal Tiger.", random.randint(5,15)

    if "national" in q and "bird" in q and "india" in q:
        return "The national bird of India is the Indian Peacock.", random.randint(5,15)

    if "national" in q and "flower" in q and "india" in q:
        return "The national flower of India is the Lotus.", random.randint(5,15)

    if "national" in q and "fruit" in q and "india" in q:
        return "The national fruit of India is the Mango.", random.randint(5,15)

    if "national" in q and "tree" in q and "india" in q:
        return "The national tree of India is the Banyan Tree.", random.randint(5,15)


    # --------- EDUCATION / PROGRAMMING ---------

    if "java" in q:
        return "Java is a high level object oriented programming language used for web and enterprise applications.", random.randint(10,20)

    if "python" in q:
        return "Python is a programming language widely used in AI, data science and automation.", random.randint(10,20)

    if "data structure" in q:
        return "A data structure is a way of organizing and storing data efficiently.", random.randint(10,20)

    if "algorithm" in q:
        return "An algorithm is a step-by-step procedure used to solve a problem.", random.randint(10,20)


    # --------- GK ---------

    if "capital" in q and "india" in q:
        return "The capital of India is New Delhi.", random.randint(5,15)

    if "largest ocean" in q:
        return "The Pacific Ocean is the largest ocean on Earth.", random.randint(5,15)


    # --------- SPORTS ---------

    if "cricket" in q:
        return "Cricket is a bat-and-ball sport played between two teams of eleven players.", random.randint(10,20)

    if "football" in q:
        return "Football is a team sport played with a spherical ball between two teams.", random.randint(10,20)


    # --------- POLITICS ---------

    if "prime minister" in q and "india" in q:
        return "The Prime Minister of India is Narendra Modi.", random.randint(40,60)

    if "president" in q and "india" in q:
        return "The President of India is Droupadi Murmu.", random.randint(40,60)


    # --------- HEALTH ---------

    if "health" in q:
        return "Health refers to the overall physical, mental and social well-being of a person.", random.randint(10,25)


    # --------- ANIMALS / BIRDS ---------

    if "animal" in q:
        return "Animals are living organisms that belong to the kingdom Animalia.", random.randint(10,25)

    if "bird" in q:
        return "Birds are warm-blooded vertebrates characterized by feathers and wings.", random.randint(10,25)


    # --------- DEFAULT ---------

    return f"This system generated an AI response related to: {question}", random.randint(15,35)



# ---------------- HALLUCINATION LEVEL ---------------- #

def get_level(score):

    if score <= 30:
        return "low"
    elif score <= 60:
        return "medium"
    else:
        return "high"



# ---------------- ROUTES ---------------- #

@app.route("/")
def home():
    return redirect("/chat")


@app.route("/chat", methods=["GET","POST"])
def chat():

    question = None
    answer = None
    score = None
    level = None

    if request.method == "POST":

        question = request.form.get("question")

        files = request.files.getlist("image")

        # -------- MULTIPLE IMAGE -------- #

        if files and files[0].filename != "":

            filenames = []

            for file in files[:5]:

                filename = file.filename
                path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(path)

                filenames.append(filename)

            question = "Images uploaded: " + ", ".join(filenames)

            answer = f"{len(filenames)} images uploaded successfully. Image recognition is simulated in this demo."

            score = random.randint(10,40)

        else:

            answer, score = get_ai_answer(question)

        level = get_level(score)

        history.append({
            "question":question,
            "answer":answer,
            "score":score,
            "level":level
        })


    return render_template("index.html",
                           question=question,
                           answer=answer,
                           score=score,
                           level=level,
                           history=history)



@app.route("/history/<int:id>")
def history_page(id):

    item = history[id]

    return render_template("index.html",
                           question=item["question"],
                           answer=item["answer"],
                           score=item["score"],
                           level=item["level"],
                           history=history)



@app.route("/logout")
def logout():
    return redirect("/chat")


if __name__ == "__main__":
    app.run(debug=True)