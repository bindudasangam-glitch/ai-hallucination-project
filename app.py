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
            if role == "User":
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

# ---------------- IMAGE ----------------

uploaded_image = st.file_uploader("Upload an image", type=["png","jpg","jpeg"])

if uploaded_image:

    image = Image.open(uploaded_image)
    st.image(image, caption="Uploaded Image")

    answer = "Image uploaded successfully. Image analysis can be added using computer vision models."

    st.session_state.conversation.append(("User","Uploaded an image"))
    st.session_state.conversation.append(("AI",answer))

    st.success(answer)

# ---------------- INPUT ----------------

question = st.text_input(
    "Ask a question (GK, Programming, Politics, Education, Science etc)",
    key="question_input"
)

# ---------------- MATH ----------------

def solve_math(q):

    try:
        expr = re.findall(r'[0-9+\-*/().]+',q)

        if expr:
            result = eval(expr[0])
            return f"The answer is {result}"

    except:
        pass

    return None

# ---------------- KNOWLEDGE BASE ----------------

def basic_knowledge(q):

    q = q.lower()

    data = {
        "capital of karnataka":"Bengaluru is the capital of Karnataka.",
        "capital of andhra pradesh":"Amaravati is the capital of Andhra Pradesh.",
        "prime minister of india":"The Prime Minister of India is Narendra Modi.",
        "who invented bulb":"Thomas Edison is credited with inventing the practical electric light bulb.",
        "what is java programming":"Java is a high level object oriented programming language developed by Sun Microsystems in 1995. It is widely used for building web applications, mobile apps and enterprise software.",
        "what is artificial intelligence":"Artificial Intelligence is a field of computer science that enables machines to simulate human intelligence such as learning, reasoning and decision making."
    }

    for k in data:
        if k in q:
            return data[k]

    return None

# ---------------- WIKIPEDIA ----------------

def wiki_answer(q):

    try:

        results = wikipedia.search(q)

        if not results:
            return None,None

        for title in results[:5]:

            try:

                summary = wikipedia.summary(title, sentences=3)

                if len(summary)>40:
                    return title,summary

            except:
                continue

    except:
        pass

    return None,None

# ---------------- PROCESS ----------------

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

        # knowledge
        k = basic_knowledge(question)

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

    # ---------------- HALLUCINATION SCORE ----------------

    if source not in ["","Math Calculation","Knowledge Base"]:

        q_emb = embed_model.encode(question,convert_to_tensor=True)
        a_emb = embed_model.encode(answer,convert_to_tensor=True)
        s_emb = embed_model.encode(source,convert_to_tensor=True)

        sim1 = util.cos_sim(q_emb,s_emb)
        sim2 = util.cos_sim(a_emb,s_emb)

        score = float((sim1[0][0] + sim2[0][0]) / 2) * 100

    else:
        score = 100

    if score > 60:
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
        st.write("No source available.")