import streamlit as st
from groq import Groq
from gtts import gTTS
import os
import uuid

# ----------------------------
# 🔑 Load API Key from Secrets
# ----------------------------
groq_client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# ----------------------------
# 🗂️ Ensure folders exist
# ----------------------------
os.makedirs("static/audio", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

# ----------------------------
# 🎧 Transcription Function
# ----------------------------
def transcribe_audio(filepath):
    if not os.path.exists(filepath):
        return "No audio file found."

    try:
        with open(filepath, "rb") as f:
            response = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",  # ✅ updated model name
                file=f,
            )
        return response.text
    except Exception as e:
        return f"⚠️ Error during transcription: {e}"

# ----------------------------
# 💬 Get AI Answer Function
# ----------------------------
def get_answer(question):
    if not question or not question.strip():
        return "Please provide a valid question."

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # ✅ updated model name
            messages=[
                {"role": "system", "content": "You are a helpful agriculture chatbot for Indian farmers. Give short, practical, and clear answers in simple English or Hindi if needed."},
                {"role": "user", "content": question}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error communicating with AI: {e}"

# ----------------------------
# 🔊 Text-to-Speech Function
# ----------------------------
def text_to_speech(text):
    filename = f"{uuid.uuid4().hex}.mp3"
    path = os.path.join("static/audio", filename)
    tts = gTTS(text)
    tts.save(path)
    return path

# ----------------------------
# 🌾 Streamlit UI
# ----------------------------
st.set_page_config(page_title="Agriculture Chatbot", layout="centered")

st.title("🌾 Agriculture Chatbot")
st.write("Ask your farming questions — type or upload your voice question below!")

option = st.radio("Choose input type:", ("Text", "Audio"))

# ----------------------------
# 📝 Text Mode
# ----------------------------
if option == "Text":
    question = st.text_input("Enter your question:")
    if st.button("Ask"):
        if question.strip():
            with st.spinner("🤖 Thinking..."):
                answer = get_answer(question)
                if "⚠️" not in answer:
                    audio_path = text_to_speech(answer)
                    st.success("✅ Answer received!")
                    st.markdown("**📝 Answer:**")
                    st.write(answer)
                    st.audio(audio_path)
                else:
                    st.error(answer)
        else:
            st.warning("Please enter a question before submitting.")

# ----------------------------
# 🎤 Audio Mode
# ----------------------------
elif option == "Audio":
    audio_file = st.file_uploader("Upload your voice question", type=["mp3", "wav", "m4a"])
    if st.button("Submit Audio"):
        if audio_file:
            filepath = os.path.join("uploads", audio_file.name)
            with open(filepath, "wb") as f:
                f.write(audio_file.read())

            with st.spinner("🎧 Transcribing and answering..."):
                transcribed = transcribe_audio(filepath)
                if "⚠️" in transcribed:
                    st.error(transcribed)
                else:
                    answer = get_answer(transcribed)
                    if "⚠️" not in answer:
                        audio_path = text_to_speech(answer)
                        st.success("✅ Answer ready!")
                        st.markdown("**🎤 Transcribed Question:**")
                        st.write(transcribed)
                        st.markdown("**📝 Answer:**")
                        st.write(answer)
                        st.audio(audio_path)
                    else:
                        st.error(answer)
        else:
            st.warning("Please upload an audio file first.")
