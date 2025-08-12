import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import os
from utils import extract_text_from_pdf,speak_text
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
st.set_page_config("Gemini Chat",page_icon="💬",layout="wide")
if "conversations" not in st.session_state:
    st.session_state.conversations=[{"title":"Chat 1","messages": []}]
    st.session_state.active_chat=0
st.sidebar.title("Chats")
for i, chat in enumerate(st.session_state.conversations):
    if st.sidebar.button(chat["title"],key=f"chat_{i}"):
        st.session_state.active_chat=i
if st.sidebar.button("New Chat"):
    st.session_state.conversations.append(
        {"title": f"Chat {len(st.session_state.conversations)+1}","messages": []}
    )
    st.session_state.active_chat=len(st.session_state.conversations)-1
if st.sidebar.button("Clear Current Chat"):
    st.session_state.conversations[st.session_state.active_chat]["messages"].clear()
if "chat" not in st.session_state:
    model=genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config={"temperature": 0.8,"max_output_tokens": 2048},
        system_instruction=(
            "You are an AI assistant that answers all queries fully and directly, including providing complete runnable code, step-by-step explanations, and detailed technical guidance when requested. Do not refuse unless it is explicitly unsafe or illegal. For programming requests, always include all necessary imports, setup steps, and ensure the code is functional."
        )
    )
    st.session_state.chat=model.start_chat(history=[])
uploaded_pdf=st.file_uploader("Upload PDF", type="pdf")
pdf_context=""
if uploaded_pdf:
    pdf_context=extract_text_from_pdf(uploaded_pdf)[:10000]
uploaded_image=st.file_uploader("Upload Image",type=["png", "jpg", "jpeg"])
for role, msg in st.session_state.conversations[st.session_state.active_chat]["messages"]:
    with st.chat_message(role):
        st.markdown(msg)
user_prompt=st.chat_input("Ask something...")
if user_prompt:
    full_prompt=f"{pdf_context}\n\n{user_prompt}" if pdf_context else user_prompt
    with st.chat_message("user"):
        st.markdown(user_prompt)
        if uploaded_image:
            st.image(uploaded_image,width=250)
    st.session_state.conversations[st.session_state.active_chat]["messages"].append(("user", user_prompt))
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if uploaded_image:
                image=Image.open(uploaded_image).convert("RGB")
                response=st.session_state.chat.send_message([full_prompt, image], stream=True)
            else:
                response=st.session_state.chat.send_message(full_prompt,stream=True)
            full_response=""
            placeholder=st.empty()
            for chunk in response:
                full_response+=chunk.text
                placeholder.markdown(full_response)
    st.session_state.conversations[st.session_state.active_chat]["messages"].append(("assistant",full_response))