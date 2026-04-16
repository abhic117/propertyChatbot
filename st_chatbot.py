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
        rows = retrieval_utils.retrieve_relevant_rows(prompt, df)
        rows = rows[['purchase_price', 'address', 'post_code']].head(1)

        address = rows.iloc[0]["address"]
        postcode = rows.iloc[0]["post_code"]
        lat, lon = osm_utils.query_coords(address, postcode)

        try:
            overpass_data = osm_utils.query_overpass(lat, lon)
        except:
            overpass_data = osm_utils.query_overpass(lat, lon)

        summary = osm_utils.summarise_amenities(overpass_data)
        ammenities_text = osm_utils.amenities_to_text(summary)
        
        context = rows.to_string(index=False)

        llm_prompt = f"""
        You are a real estate assistant helping a user with property related questions.

        Answer using only the data provided. 

        DATA:
        {context}

        {ammenities_text}

        QUESTION:
        {prompt}
        """

        result = ollama.chat(
            model="qwen2.5:7b-instruct-q4_K_M",
            messages=[{"role": "user", "content": llm_prompt}]
        )
        st.write(stream_data(result["message"]["content"]))