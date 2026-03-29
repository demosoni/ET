import streamlit as st
import requests

st.set_page_config(page_title="KrishiSaarthi AI 🌾", layout="wide")

st.title("🌾 KrishiSaarthi AI")
st.caption("Conversational Farming Assistant 🇮🇳")

# ===== SESSION =====
if "messages" not in st.session_state:
    st.session_state.messages = []

# ===== LOCATION + CROP =====
col1, col2 = st.columns(2)
with col1:
    location = st.text_input("📍 Location")
with col2:
    crop = st.text_input("🌾 Crop")

# ===== DISPLAY CHAT =====
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ===== 🎤 DIRECT MIC INPUT (NO UPLOAD) =====
st.markdown("### 🎤 Voice Input")

audio_bytes = st.audio_input("🎙️ Tap to record")

def voice_to_text_api(audio_bytes):
    try:
        url = "https://api-inference.huggingface.co/models/openai/whisper-small"

        response = requests.post(
            url,
            headers={"Authorization": "Bearer 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"},
            data=audio_bytes,
            timeout=20
        )

        if response.status_code == 200:
            return response.json().get("text", None)
        else:
            return None

    except:
        return None

# Process voice input
if audio_bytes:
    if "voice_used" not in st.session_state:
        st.session_state["voice_used"] = True

        with st.spinner("Processing voice..."):
            text = voice_to_text_api(audio_bytes)

        if text:
            st.success(f"🗣️ {text}")
            st.session_state.messages.append({"role": "user", "content": text})
            st.rerun()
        else:
            st.error("Voice not recognized. Try again.")

# ===== CHAT INPUT =====
user_input = st.chat_input("Ask your farming question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

# ===== RESPONSE =====
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":

    query = st.session_state.messages[-1]["content"]

    try:
        res = requests.post(
            "http://127.0.0.1:8000/ask",
            json={
                "query": query,
                "location": location,
                "crop": crop
            },
            timeout=15
        )

        if res.status_code == 200:
            response = res.json().get("response", "No response")
        else:
            response = "⚠️ Server issue. Try again."

    except:
        response = "⚠️ Backend not reachable"

    st.session_state.messages.append({"role": "assistant", "content": response})

    # Reset voice flag after response
    if "voice_used" in st.session_state:
        del st.session_state["voice_used"]

    st.rerun()