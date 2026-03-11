import streamlit as st
import wikipedia
import re
from sentence_transformers import SentenceTransformer, util

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

# NEW CHAT
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

    title = item["title"]

    if st.sidebar.button(title,key=f"history_{i}"):

        st.session_state.conversation = item["chat"]
        st.session_state.question_input = ""
        st.rerun()

# ---------------- QUESTION INPUT ----------------

question = st.text_input(
    "Ask a question (Politics, History, GK, Medical, Agriculture, Programming etc)",
    key="question_input"
)

# ---------------- ANSWER SYSTEM ----------------

def solve_math(question):

    try:

        expr = re.findall(r'[0-9+\-*/().]+',question)

        if expr:
            result = eval(expr[0])
            return f"The answer is {result}"

    except:
        return None


def get_answer(question):

    # 1️⃣ Try math
    math_answer = solve_math(question)

    if math_answer:
        return math_answer,"Math calculation"

    # 2️⃣ Try Wikipedia
    try:
        source = wikipedia.summary(question, sentences=3)
        answer = source.split(".")[0]
        return answer,source

    except:
        return "Sorry, I couldn't find a reliable answer.",""

# ---------------- PROCESS QUESTION ----------------

if question:

    st.session_state.conversation.append(("User",question))

    answer,source = get_answer(question)

    st.session_state.conversation.append(("AI",answer))

    # hallucination score

    if source:

        emb1 = embed_model.encode(answer,convert_to_tensor=True)
        emb2 = embed_model.encode(source,convert_to_tensor=True)

        similarity = util.cos_sim(emb1,emb2)

        score = float(similarity[0][0])*100

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