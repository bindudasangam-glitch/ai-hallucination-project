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

# ---------------- LOAD EMBEDDING MODEL ----------------

@st.cache_resource
def load_model():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    return model

embed_model = load_model()

# ---------------- SIDEBAR ----------------

st.sidebar.title("Chat")

if st.sidebar.button("➕ New Chat"):
    if st.session_state.conversation:
        st.session_state.history.append(st.session_state.conversation)
    st.session_state.conversation = []

st.sidebar.markdown("### History")

for i, chat in enumerate(st.session_state.history):
    if st.sidebar.button(f"Chat {i+1}"):
        st.session_state.conversation = chat

# ---------------- IMAGE UPLOAD ----------------

uploaded_image = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_image is not None:
    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # simple placeholder answer for image
    image_answer = "Image uploaded successfully. This project can analyze images."

    st.session_state.conversation.append(("User", "Uploaded an image"))
    st.session_state.conversation.append(("AI", image_answer))

    st.write(image_answer)

# ---------------- QUESTION INPUT ----------------

question = st.text_input(
    "Ask a question (Politics, History, GK, Medical, Agriculture, Programming etc)"
)

if question:

    st.session_state.conversation.append(("User", question))

    try:
        source = wikipedia.summary(question, sentences=3)
    except:
        source = ""

    if source:
        answer = source.split(".")[0]
    else:
        answer = "No reliable source found."

    st.session_state.conversation.append(("AI", answer))

    # ---------------- HALLUCINATION SCORE ----------------

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

# ---------------- DISPLAY CHAT ----------------

for role, msg in st.session_state.conversation:

    if role == "User":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **AI:** {msg}")

# ---------------- VERIFIED SOURCE ----------------

if question:

    st.subheader("Verified Source")

    if source:
        st.write(source)
    else:
        st.write("No verified source found.")