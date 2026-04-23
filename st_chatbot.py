import streamlit as st
import ollama
import time
import pandas as pd
import json

import retrieval_utils

PROCESSED_FILE = "processed_nsw_property_data.parquet"
JSON_AMENITY_DATA = "postcode_amenity_data.json"

df = pd.read_parquet(PROCESSED_FILE)
amenity_file = JSON_AMENITY_DATA

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
        amenities = ''
        score = ''

        query_intent = retrieval_utils.detect_intent(prompt)
        print(query_intent)

        # Chooses a retrieval method based on the detected intent of the prompt
        match query_intent:
            case 'price': 
                rows = retrieval_utils.price_query_retrieval(prompt, df)
            case 'amenity':
                rows = retrieval_utils.amenity_query_retrieval(prompt, df)

                with open(amenity_file) as f:
                    data = json.load(f)
                postcode = str(rows['post_code'].item())
                
                amenities = data[str(postcode)]['amenities']
                score = data[postcode]['amenity_score']

                print(amenities, score)

        context = rows.to_string(index=False)

        llm_prompt = f"""
        You are a real estate assistant helping a user with property related questions.

        Answer using only the data provided.

        Answer in a human tone, as if you are a human assistant answering customer questions.

        DATA:
        {context}

        {amenities}

        {score}

        QUESTION:
        {prompt}
        """

        result = ollama.chat(
            model="qwen2.5:7b-instruct-q4_K_M",
            messages=[{"role": "user", "content": llm_prompt}]
        )
        st.write(stream_data(result["message"]["content"]))