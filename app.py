import streamlit as st
import wikipedia
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
from PIL import Image
import torch

st.set_page_config(page_title="AI Hallucination Detection System", layout="wide")

st.title("🔎 AI Hallucination Detection System")

# -------------------------------
# SESSION STATE
# -------------------------------

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "history" not in st.session_state:
    st.session_state.history = []

# -------------------------------
# LOAD MODELS
# -------------------------------

@st.cache_resource
def load_models():

    generator = pipeline(
        "text2text-generation",
        model="google/flan-t5-base"
    )

    embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    image_model = pipeline(
        "image-to-text",
        model="Salesforce/blip-image-captioning-base"
    )

    return generator, embed_model, image_model


generator, embed_model, image_model = load_models()

# -------------------------------
# SIDEBAR
# -------------------------------

st.sidebar.title("Chat")

if st.sidebar.button("➕ New Chat"):

    if st.session_state.conversation:
        st.session_state.history.append(st.session_state.conversation)

    st.session_state.conversation = []

st.sidebar.markdown("### History")

for i, chat in enumerate(st.session_state.history):

    if st.sidebar.button(f"Chat {i+1}"):

        st.session_state.conversation = chat


# -------------------------------
# QUESTION INPUT
# -------------------------------

question = st.text_input(
    "Ask a question (Politics, History, GK, Medical, Agriculture, Programming etc)"
)

# -------------------------------
# IMAGE UPLOAD
# -------------------------------

uploaded_image = st.file_uploader("Upload an image", type=["png","jpg","jpeg"])

# -------------------------------
# IMAGE QUESTION
# -------------------------------

if uploaded_image is not None:

    image = Image.open(uploaded_image)

    st.image(image, caption="Uploaded Image")

    caption = image_model(image)[0]["generated_text"]

    st.subheader("Image Description")
    st.write(caption)

    st.session_state.conversation.append(("User","Image uploaded"))
    st.session_state.conversation.append(("AI",caption))


# -------------------------------
# TEXT QUESTION
# -------------------------------

if question:

    st.session_state.conversation.append(("User", question))

    try:
        source = wikipedia.summary(question, sentences=3)
    except:
        source = ""

    prompt = f"Answer this question clearly: {question}"

    result = generator(prompt, max_length=120)

    answer = result[0]["generated_text"]

    st.session_state.conversation.append(("AI", answer))

    # -------------------------------
    # HALLUCINATION SCORE
    # -------------------------------

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

# -------------------------------
# SHOW CHAT
# -------------------------------

for role, msg in st.session_state.conversation:

    if role == "User":
        st.markdown(f"🧑 **You:** {msg}")

    else:
        st.markdown(f"🤖 **AI:** {msg}")

# -------------------------------
# VERIFIED SOURCE
# -------------------------------

if question:

    st.subheader("Verified Source")

    if source:

        st.write(source)

    else:

        st.write("No verified source found.")