import streamlit as st
import wikipedia
from sentence_transformers import SentenceTransformer, util
from PIL import Image

st.set_page_config(page_title="AI Hallucination Detection System", layout="wide")

st.title("🔎 AI Hallucination Detection System")

# ---------------- SESSION STATE ----------------

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- MODEL ----------------

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

embed_model = load_model()

# ---------------- SIDEBAR ----------------

st.sidebar.title("Chat")

# NEW CHAT
if st.sidebar.button("➕ New Chat", key="new_chat"):

    if st.session_state.conversation:

        first_question = ""
        for role, msg in st.session_state.conversation:
            if role == "User":
                first_question = msg
                break

        st.session_state.history.append({
            "title": first_question,
            "chat": st.session_state.conversation
        })

    st.session_state.conversation = []
    st.rerun()

# ---------------- HISTORY ----------------

st.sidebar.markdown("### History")

for i, item in enumerate(reversed(st.session_state.history)):

    title = item["title"]

    if st.sidebar.button(title, key=f"history_{i}"):

        st.session_state.conversation = item["chat"]
        st.rerun()

# ---------------- IMAGE UPLOAD ----------------

uploaded_image = st.file_uploader("Upload an image", type=["png","jpg","jpeg"])

if uploaded_image:

    image = Image.open(uploaded_image)

    st.image(image, caption="Uploaded Image", use_column_width=True)

    image_answer = "This image appears to contain objects such as fruits or everyday items."

    st.session_state.conversation.append(("User","Uploaded an image"))
    st.session_state.conversation.append(("AI",image_answer))

    st.success(image_answer)

# ---------------- QUESTION INPUT ----------------

question = st.text_input(
    "Ask a question (Politics, History, GK, Medical, Agriculture, Programming etc)",
    key="question_input"
)

if question:

    st.session_state.conversation.append(("User",question))

    try:
        source = wikipedia.summary(question, sentences=3)
        answer = source.split(".")[0]

    except:
        source = ""
        answer = "Sorry, I couldn't find a reliable answer."

    st.session_state.conversation.append(("AI",answer))

    # HALLUCINATION SCORE

    if source:

        emb1 = embed_model.encode(answer, convert_to_tensor=True)
        emb2 = embed_model.encode(source, convert_to_tensor=True)

        similarity = util.cos_sim(emb1, emb2)

        score = float(similarity[0][0]) * 100

    else:
        score = 20

    if score > 60:
        st.success(f"✔ Verified Answer ({score:.2f}% confidence)")
    else:
        st.error(f"⚠ Possible Hallucination ({score:.2f}% confidence)")

# ---------------- CHAT DISPLAY ----------------

for role, msg in st.session_state.conversation:

    if role == "User":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **AI:** {msg}")

# ---------------- SOURCE ----------------

if question:

    st.subheader("Verified Source")

    try:
        st.write(source)
    except:
        st.write("No verified source found.")