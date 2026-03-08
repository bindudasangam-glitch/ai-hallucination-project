from flask import Flask, render_template, request
import os
import random
import re
import pytesseract
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

history = []


# ---------------- AI ANSWER FUNCTION ---------------- #

def get_ai_answer(question):

    q = question.lower()

    # -------- MATH DETECTION -------- #

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


    # -------- GK / GENERAL -------- #

    if "national animal" in q and "india" in q:
        return "The national animal of India is the Bengal Tiger.", random.randint(5,15)

    if "national bird" in q and "india" in q:
        return "The national bird of India is the Indian Peacock.", random.randint(5,15)

    if "capital" in q and "india" in q:
        return "The capital of India is New Delhi.", random.randint(5,15)


    # -------- EDUCATION -------- #

    if "java" in q:
        return "Java is a high level object oriented programming language used for web and enterprise applications.", random.randint(10,20)

    if "python" in q:
        return "Python is a programming language widely used in AI, data science and automation.", random.randint(10,20)

    if "data structure" in q:
        return "A data structure is a way of organizing and storing data efficiently.", random.randint(10,20)

    if "oop" in q:
        return "Object Oriented Programming (OOP) is a programming paradigm based on objects, classes, inheritance, encapsulation and polymorphism.", random.randint(10,20)


    # -------- SPORTS -------- #

    if "cricket" in q:
        return "Cricket is a bat and ball sport played between two teams of eleven players.", random.randint(10,20)

    if "football" in q:
        return "Football is a team sport played with a spherical ball between two teams.", random.randint(10,20)


    # -------- POLITICS -------- #

    if "prime minister" in q and "india" in q:
        return "The Prime Minister of India is Narendra Modi.", random.randint(40,60)

    if "president" in q and "india" in q:
        return "The President of India is Droupadi Murmu.", random.randint(40,60)


    # -------- DEFAULT -------- #

    return f"Based on available knowledge, the answer related to '{question}' requires further explanation.", random.randint(15,35)



# ---------------- HALLUCINATION LEVEL ---------------- #

def get_level(score):

    if score <= 30:
        return "low"
    elif score <= 60:
        return "medium"
    else:
        return "high"



# ---------------- MAIN ROUTE ---------------- #

@app.route("/", methods=["GET","POST"])
def home():

    question = None
    answer = None
    score = None
    level = None

    if request.method == "POST":

        question = request.form.get("question")

        files = request.files.getlist("image")

        # -------- IMAGE OCR -------- #

        if files and files[0].filename != "":

            detected_text = ""

            for file in files[:5]:

                filename = file.filename
                path = os.path.join(UPLOAD_FOLDER, filename)

                file.save(path)

                img = Image.open(path)

                text = pytesseract.image_to_string(img)

                detected_text += text + " "

            question = detected_text.strip()

            if question == "":
                answer = "No readable text found in the image."
                score = random.randint(20,40)
            else:
                answer, score = get_ai_answer(question)

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



if __name__ == "__main__":
    app.run(debug=True)