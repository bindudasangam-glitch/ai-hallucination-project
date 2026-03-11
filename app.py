import streamlit as st
import wikipedia
import re
from sentence_transformers import SentenceTransformer, util
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

st.set_page_config(page_title="AI Hallucination Detection", layout="wide")

st.title("🔎 AI Hallucination Detection System")

# ---------------- SESSION ----------------

if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "history" not in st.session_state:
    st.session_state.history = []

if "image_caption" not in st.session_state:
    st.session_state.image_caption = None

# ---------------- MODELS ----------------

@st.cache_resource
def load_models():

    embed = SentenceTransformer("all-MiniLM-L6-v2")

    processor = BlipProcessor.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    )

    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-base"
    )

    return embed, processor, model


embed_model, blip_processor, blip_model = load_models()

# ---------------- SIDEBAR ----------------

st.sidebar.title("Chat")

if st.sidebar.button("➕ New Chat"):

    if st.session_state.conversation:

        first = ""

        for r,m in st.session_state.conversation:
            if r=="User":
                first=m
                break

        st.session_state.history.append({
            "title":first,
            "chat":st.session_state.conversation
        })

    st.session_state.conversation=[]
    st.session_state.image_caption=None
    st.rerun()

st.sidebar.markdown("### History")

for i,item in enumerate(reversed(st.session_state.history)):

    if st.sidebar.button(item["title"],key=i):

        st.session_state.conversation=item["chat"]
        st.rerun()

# ---------------- IMAGE UPLOAD ----------------

uploaded = st.file_uploader("Upload an image", type=["png","jpg","jpeg"])

if uploaded:

    image = Image.open(uploaded).convert("RGB")

    st.image(image)

    inputs = blip_processor(image, return_tensors="pt")

    out = blip_model.generate(**inputs)

    caption = blip_processor.decode(out[0], skip_special_tokens=True)

    st.session_state.image_caption = caption

    st.success(f"Image detected: {caption}")

# ---------------- INPUT ----------------

question = st.text_input("Ask a question")

# ---------------- MATH ----------------

def solve_math(q):

    try:

        expr = re.findall(r"[0-9\+\-\*\/\(\)]+",q)

        if expr:
            return eval(expr[0])

    except:
        pass

    return None

# ---------------- WIKI ----------------

def wiki_answer(q):

    try:

        results = wikipedia.search(q)

        if results:

            title = results[0]

            summary = wikipedia.summary(title, sentences=3)

            ans = summary.split(".")[0]+"."

            return ans, summary

    except:
        pass

    return None,None

# ---------------- PROCESS ----------------

if question:

    st.session_state.conversation.append(("User",question))

    source=""

    # IMAGE QUESTION

    if st.session_state.image_caption:

        combined_query = st.session_state.image_caption+" "+question

        ans,source = wiki_answer(combined_query)

        if not ans:
            ans = f"The image likely shows {st.session_state.image_caption}"

    else:

        math = solve_math(question)

        if math is not None:

            ans = f"The answer is {math}"
            source = str(math)

        else:

            ans,source = wiki_answer(question)

            if not ans:
                ans="Sorry, I couldn't find a reliable answer."

    st.session_state.conversation.append(("AI",ans))

    # ---------------- HALLUCINATION ----------------

    if source:

        q_emb = embed_model.encode(question,convert_to_tensor=True)

        a_emb = embed_model.encode(ans,convert_to_tensor=True)

        s_emb = embed_model.encode(source,convert_to_tensor=True)

        sim1 = util.cos_sim(q_emb,s_emb)

        sim2 = util.cos_sim(a_emb,s_emb)

        score = float((sim1[0][0]+sim2[0][0])/2)*100

    else:

        score = 20

    if score>60:
        st.success(f"✔ Verified Answer ({score:.2f}% confidence)")
    else:
        st.error(f"⚠ Possible Hallucination ({score:.2f}% confidence)")

# ---------------- CHAT ----------------

for role,msg in st.session_state.conversation:

    if role=="User":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **AI:** {msg}")

# ---------------- SOURCE ----------------

if question:

    st.subheader("Verified Source")

    if source:
        st.write(source)
    else:
        st.write("No source available")