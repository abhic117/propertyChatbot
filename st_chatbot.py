import streamlit as st
import ollama
import time

import preprocess_utils
import retrieval_utils
import osm_utils

RAW_FILE = "nsw_property_data.csv"
PROCESSED_FILE = "processed_nsw_property_data.parquet"

df = preprocess_utils.load_data(RAW_FILE, PROCESSED_FILE)

# Make text flow
def stream_data(text, delay:float=0.02):
    for word in text.split():
        yield word + " "
        time.sleep(delay)

# Prompt input
prompt = st.chat_input("Ask anything")

if prompt:
    # Diplay input prompt
    with st.chat_message("user"):
        st.write(prompt)

    # Processing
    with st.spinner("Thinking..."):
        amenities_text = ''
        query_intent = retrieval_utils.detect_intent(prompt)

        match query_intent:
            case 'price': 
                rows = retrieval_utils.price_query_retrieval(prompt, df)
            case 'amenity':
                rows = retrieval_utils.amenity_query_retrieval(prompt, df)

                amenities_text = rows.iloc[0]["amenities_text"]

        context = rows.to_string(index=False)

        llm_prompt = f"""
        You are a real estate assistant helping a user with property related questions.

        Answer using only the data provided. 

        DATA:
        {context}

        {amenities_text}

        QUESTION:
        {prompt}
        """

        result = ollama.chat(
            model="qwen2.5:7b-instruct-q4_K_M",
            messages=[{"role": "user", "content": llm_prompt}]
        )
        st.write(stream_data(result["message"]["content"]))