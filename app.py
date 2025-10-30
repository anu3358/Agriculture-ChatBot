import streamlit as st
from groq import Groq
from gtts import gTTS
import os
import uuid

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="Agriculture Chatbot", layout="centered")
st.title("🌾 Agriculture Chatbot")
st.write("Ask your farming questions — type or upload your voice question below!")

# ----------------------------
# Load API Key securely (Streamlit Secrets or environment)
# ----------------------------
api_key = st.secrets.get("GROQ_API_KEY", os.getenv("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"))

if not api_key:
    st.error("🚨 Missing GROQ_API_KEY! Please add it in Streamlit Secrets or set the GROQ_API_KEY environment variable.")
    st.stop()

# ----------------------------
# Initialize Groq client safely
# ----------------------------
try:
    groq_client = Groq(api_key=api_key)
    st.info("✅ Groq client loaded.")
except Exception as e:
    st.error(f"❌ Could not initialize Groq client: {e}")
    st.stop()

# ----------------------------
# Ensure directories exist
# ----------------------------
os.makedirs("static/audio", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# ----------------------------
# Transcription: audio -> text
# ----------------------------
def transcribe_audio(filepath):
    if not os.path.exists(filepath):
        return "⚠️ No audio file found."

    try:
        with open(filepath, "rb") as f:
            response = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",  # correct model name
                file=f,
            )
        # response.text contains the transcription
        return response.text
    except Exception as e:
        return f"⚠️ Error during transcription: {e}"

# ----------------------------
# Chat completion: question -> answer
# ----------------------------
def get_answer(question):
    if not question or not question.strip():
        return "Please provide a valid question."

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # correct model name
            messages=[
                {"role": "system", "content": "You are a helpful agriculture chatbot for Indian farmers. Give short, practical, and clear answers in simple English or Hindi."},
                {"role": "user", "content": question}
            ],
        )
        # Depending on SDK response shape
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error communicating with AI: {e}"

# ----------------------------
# Text-to-speech
# ----------------------------
def text_to_speech(text):
    filename = f"{uuid.uuid4().hex}.mp3"
    path = os.path.join("static/audio", filename)
    try:
        tts = gTTS(text)
        tts.save(path)
        return path
    except Exception as e:
        return None

# ----------------------------
# UI: Input choice
# ----------------------------
option = st.radio("Choose input type:", ("Text", "Audio"))

# Text mode
if option == "Text":
    question = st.text_input("Enter your question:")
    if st.button("Ask"):
        if not question or not question.strip():
            st.warning("Please enter a question before submitting.")
        else:
            with st.spinner("🤖 Thinking..."):
                answer = get_answer(question)
                if answer.startswith("⚠️"):
                    st.error(answer)
                else:
                    audio_path = text_to_speech(answer)
                    st.success("✅ Answer received!")
                    st.markdown("**📝 Answer:**")
                    st.write(answer)
                    if audio_path:
                        st.audio(audio_path)

# Audio mode
elif option == "Audio":
    audio_file = st.file_uploader("Upload your voice question", type=["mp3", "wav", "m4a"])
    if st.button("Submit Audio"):
        if not audio_file:
            st.warning("Please upload an audio file first.")
        else:
            filepath = os.path.join("uploads", audio_file.name)
            with open(filepath, "wb") as f:
                f.write(audio_file.read())

            with st.spinner("🎧 Transcribing and answering..."):
                transcribed = transcribe_audio(filepath)
                if transcribed.startswith("⚠️"):
                    st.error(transcribed)
                else:
                    answer = get_answer(transcribed)
                    if answer.startswith("⚠️"):
                        st.error(answer)
                    else:
                        audio_path = text_to_speech(answer)
                        st.success("✅ Answer ready!")
                        st.markdown("**🎤 Transcribed Question:**")
                        st.write(transcribed)
                        st.markdown("**📝 Answer:**")
                        st.write(answer)
                        if audio_path:
                            st.audio(audio_path)


