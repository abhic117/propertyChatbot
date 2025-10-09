import streamlit as st
import ollama
import time

# make text flow
def stream_data(text, delay:float=0.02):
    for word in text.split():
        yield word + " "
        time.sleep(delay)

# prompt input
prompt = st.chat_input("Ask anything")

if prompt:
    # diplay input prompt
    with st.chat_message("user"):
        st.write(prompt)

    # Processing
    with st.spinner("Thinking..."):
        result = ollama.chat(model="tinyllama", messages=[{
            "role":"user",
            "content":prompt,
        }])
        response = result["message"]["content"]
        st.write(stream_data(response))