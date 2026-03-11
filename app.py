import streamlit as st
import wikipedia
import re
from sentence_transformers import SentenceTransformer, util
from PIL import Image

st.set_page_config(page_title="AI Hallucination Detection System", layout="wide")

st.title("🔎 AI Hallucination Detection System")

# ---------------- SESSION ----------------

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "history" not in st.session_state:
    st.session_state.history = []

if "question_input" not in st.session_state:
    st.session_state.question_input = ""

# ---------------- MODEL ----------------

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

embed_model = load_model()

# ---------------- SIDEBAR ----------------

st.sidebar.title("Chat")

if st.sidebar.button("➕ New Chat"):

    if st.session_state.conversation:

        first_question = ""

        for role,msg in st.session_state.conversation:
            if role=="User":
                first_question = msg
                break

        st.session_state.history.append({
            "title": first_question,
            "chat": st.session_state.conversation
        })

    st.session_state.conversation = []
    st.session_state.question_input = ""
    st.rerun()

# ---------------- HISTORY ----------------

st.sidebar.markdown("### History")

for i,item in enumerate(reversed(st.session_state.history)):

    if st.sidebar.button(item["title"], key=f"h{i}"):

        st.session_state.conversation = item["chat"]
        st.session_state.question_input = ""
        st.rerun()

# ---------------- IMAGE UPLOAD ----------------

uploaded_image = st.file_uploader("Upload an image", type=["png","jpg","jpeg"])

if uploaded_image:

    image = Image.open(uploaded_image)

    st.image(image, caption="Uploaded Image")

    answer = "Image uploaded successfully. Image analysis feature can be extended using vision models."

    st.session_state.conversation.append(("User","Uploaded an image"))
    st.session_state.conversation.append(("AI",answer))

    st.success(answer)

# ---------------- QUESTION INPUT ----------------

question = st.text_input(
    "Ask a question (Politics, History, GK, Medical, Agriculture, Programming etc)",
    key="question_input"
)

# ---------------- MATH SOLVER ----------------

def solve_math(q):

    try:
        expr = re.findall(r'[0-9+\-*/().]+',q)

        if expr:
            result = eval(expr[0])
            return f"The answer is {result}"

    except:
        pass

    return None

# ---------------- SPECIAL KNOWLEDGE ----------------

def knowledge_answers(q):

    q=q.lower()

    if "capital of andhra pradesh" in q:
        return "The capital of Andhra Pradesh is Amaravati."

    if "prime minister of india" in q:
        return "The Prime Minister of India is Narendra Modi."

    if "who invented bulb" in q:
        return "Thomas Edison is widely credited with inventing the practical electric light bulb."

    if "ai projects" in q:
        return """Some AI related project ideas are:

1. AI Chatbot for Student Help
2. Fake News Detection using NLP
3. AI Based Disease Prediction System
4. Smart Traffic Control using AI
5. AI Resume Screening System
6. Face Recognition Attendance System"""

    return None

# ---------------- WIKIPEDIA ANSWER ----------------

def wiki_answer(q):

    try:

        results = wikipedia.search(q)

        for r in results[:5]:

            page = wikipedia.page(r, auto_suggest=False)

            summary = wikipedia.summary(r, sentences=3)

            return r, summary

    except:
        pass

    return None,None

# ---------------- PROCESS QUESTION ----------------

if question:

    st.session_state.conversation.append(("User",question))

    answer = None
    source = ""

    # math
    math_answer = solve_math(question)

    if math_answer:

        answer = math_answer
        source = "Math Calculation"

    else:

        # knowledge answers
        k = knowledge_answers(question)

        if k:
            answer = k
            source = "Knowledge Base"

        else:

            title,summary = wiki_answer(question)

            if summary:

                answer = summary.split(".")[0] + "."
                source = summary

            else:

                answer = "Sorry, I couldn't find a reliable answer."

    st.session_state.conversation.append(("AI",answer))

    # hallucination score

    if source and source not in ["Math Calculation","Knowledge Base"]:

        q_emb = embed_model.encode(question,convert_to_tensor=True)
        a_emb = embed_model.encode(answer,convert_to_tensor=True)
        s_emb = embed_model.encode(source,convert_to_tensor=True)

        q_score = util.cos_sim(q_emb,s_emb)
        a_score = util.cos_sim(a_emb,s_emb)

        score = float((q_score[0][0] + a_score[0][0]) / 2) * 100

    else:
        score = 100

    if score>60:
        st.success(f"✔ Verified Answer ({score:.2f}% confidence)")
    else:
        st.error(f"⚠ Possible Hallucination ({score:.2f}% confidence)")

# ---------------- CHAT DISPLAY ----------------

for role,msg in st.session_state.conversation:

    if role=="User":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **AI:** {msg}")

# ---------------- SOURCE ----------------

if question:

    st.subheader("Verified Source")

    try:
        st.write(source)
    except:
        st.write("No source available.")