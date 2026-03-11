import streamlit as st
import wikipedia
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

st.set_page_config(page_title="AI Hallucination Detection System", layout="wide")

st.title("🔎 AI Hallucination Detection System")

# -------------------------
# Session State
# -------------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "current_question" not in st.session_state:
    st.session_state.current_question = ""

# -------------------------
# Load Models
# -------------------------

@st.cache_resource
def load_models():

    generator = pipeline(
        "text-generation",
        model="gpt2"
    )

    embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    return generator, embed_model


generator, embed_model = load_models()

# -------------------------
# Sidebar
# -------------------------

st.sidebar.title("Chat")

if st.sidebar.button("➕ New Chat"):
    st.session_state.current_question = ""

st.sidebar.markdown("### History")

for q in st.session_state.history:

    if st.sidebar.button(q):
        st.session_state.current_question = q


# -------------------------
# Input Question
# -------------------------

question = st.text_input(
    "Ask a question (Politics, History, GK, Medical, Agriculture, Programming etc)",
    value=st.session_state.current_question
)

if question:

    st.session_state.current_question = question

    if question not in st.session_state.history:
        st.session_state.history.insert(0, question)

    # -------------------------
    # Wikipedia Source
    # -------------------------

    try:
        source = wikipedia.summary(question, sentences=3)
    except:
        source = ""

    # -------------------------
    # Generate Answer
    # -------------------------

    prompt = f"Answer clearly: {question}"

    result = generator(prompt, max_length=120)

    raw_answer = result[0]["generated_text"]

    answer = raw_answer.replace(prompt, "").strip()

    if answer == "":
        answer = "No answer generated."

    # -------------------------
    # Hallucination Score
    # -------------------------

    if source:

        emb1 = embed_model.encode(answer, convert_to_tensor=True)
        emb2 = embed_model.encode(source, convert_to_tensor=True)

        similarity = util.cos_sim(emb1, emb2)

        score = float(similarity[0][0]) * 100

    else:
        score = 20

    # -------------------------
    # Result
    # -------------------------

    if score > 60:
        st.success(f"✔ Verified Answer ({score:.2f}% confidence)")
    else:
        st.error(f"⚠ Possible Hallucination ({score:.2f}% confidence)")

    # -------------------------
    # Answer
    # -------------------------

    st.subheader("Answer")
    st.write(answer)

    # -------------------------
    # Source
    # -------------------------

    st.subheader("Verified Source")

    if source:
        st.write(source)
    else:
        st.write("No verified source found.")