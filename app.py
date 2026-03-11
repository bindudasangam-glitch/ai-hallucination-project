import streamlit as st
import wikipedia
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util

st.set_page_config(page_title="AI Hallucination Detection System", layout="wide")

st.title("🔎 AI Hallucination Detection System")

# -----------------------------
# SESSION STATES
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "conversation" not in st.session_state:
    st.session_state.conversation = []

# -----------------------------
# LOAD MODELS
# -----------------------------
@st.cache_resource
def load_models():

    generator = pipeline(
        "text-generation",
        model="gpt2"
    )

    embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    return generator, embed_model


generator, embed_model = load_models()

# -----------------------------
# SIDEBAR
# -----------------------------
st.sidebar.title("Chat")

# NEW CHAT
if st.sidebar.button("➕ New Chat"):
    st.session_state.conversation = []

st.sidebar.markdown("### History")

for chat in st.session_state.chat_history:
    if st.sidebar.button(chat):
        st.session_state.conversation.append(("User", chat))

# -----------------------------
# USER INPUT
# -----------------------------
question = st.text_input(
    "Ask a question (Politics, History, GK, Medical, Agriculture, Programming etc)"
)

if question:

    # store conversation
    st.session_state.conversation.append(("User", question))
    st.session_state.chat_history.insert(0, question)

    # -----------------------------
    # WIKIPEDIA SOURCE
    # -----------------------------
    try:
        source = wikipedia.summary(question, sentences=3)
    except:
        source = ""

    # -----------------------------
    # GENERATE ANSWER
    # -----------------------------
    prompt = f"Question: {question}\nAnswer:"

    result = generator(prompt, max_length=120)

    raw = result[0]["generated_text"]

    answer = raw.replace(prompt, "").strip()

    if answer == "":
        answer = "I could not generate an answer."

    st.session_state.conversation.append(("AI", answer))

    # -----------------------------
    # HALLUCINATION SCORE
    # -----------------------------
    if source:

        emb1 = embed_model.encode(answer, convert_to_tensor=True)
        emb2 = embed_model.encode(source, convert_to_tensor=True)

        similarity = util.cos_sim(emb1, emb2)

        score = float(similarity[0][0]) * 100

    else:
        score = 20

    # -----------------------------
    # SHOW RESULT
    # -----------------------------
    if score > 60:
        st.success(f"✔ Verified Answer ({score:.2f}% confidence)")
    else:
        st.error(f"⚠ Possible Hallucination ({score:.2f}% confidence)")

# -----------------------------
# DISPLAY CHAT
# -----------------------------
for role, msg in st.session_state.conversation:

    if role == "User":
        st.markdown(f"**🧑 You:** {msg}")
    else:
        st.markdown(f"**🤖 AI:** {msg}")

# -----------------------------
# SOURCE
# -----------------------------
if question:

    st.subheader("Verified Source")

    if source:
        st.write(source)
    else:
        st.write("No verified source found.")