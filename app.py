import streamlit as st
from groq import Groq
from gtts import gTTS
import os
import uuid

groq_client = Groq(api_key="")  # Insert your Groq API key

# Ensure necessary folders exist
os.makedirs("static/audio", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

def transcribe_audio(filepath):
    with open(filepath, "rb") as f:
        response = groq_client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=f,
        )
    return response.text

def get_answer(question):
    response = groq_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful agriculture chatbot for Indian farmers."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

def text_to_speech(text):
    filename = f"{uuid.uuid4().hex}.mp3"
    path = os.path.join("static/audio", filename)
    tts = gTTS(text)
    tts.save(path)
    return path

st.set_page_config(page_title="Agriculture Chatbot", layout="centered")

st.title("🌾 Agriculture Chatbot")
st.write("Ask your farming questions by typing or uploading voice.")

option = st.radio("Choose input type:", ("Text", "Audio"))

if option == "Text":
    question = st.text_input("Enter your question:")
    if st.button("Ask"):
        if question.strip():
            with st.spinner("🤖 Thinking..."):
                answer = get_answer(question)
                audio_path = text_to_speech(answer)
                st.success("✅ Answer received!")
                st.markdown("**📝 Answer:**")
                st.write(answer)
                st.audio(audio_path)
        else:
            st.warning("Please enter a question.")

elif option == "Audio":
    audio_file = st.file_uploader("Upload your voice question", type=["mp3", "wav", "m4a"])
    if st.button("Submit Audio"):
        if audio_file:
            filepath = os.path.join("uploads", audio_file.name)
            with open(filepath, "wb") as f:
                f.write(audio_file.read())

            with st.spinner("🎧 Transcribing and answering..."):
                transcribed = transcribe_audio(filepath)
                answer = get_answer(transcribed)
                audio_path = text_to_speech(answer)

                st.success("✅ Answer ready!")
                st.markdown("**🎤 Transcribed Question:**")
                st.write(transcribed)
                st.markdown("**📝 Answer:**")
                st.write(answer)
                st.audio(audio_path)
        else:
            st.warning("Please upload an audio file.")
