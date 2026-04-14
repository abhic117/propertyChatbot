import streamlit as st
import ollama
import time
import pandas as pd

import preprocess_utils

RAW_FILE = "nsw_property_data.csv"
PROCESSED_FILE = "processed_nsw_property_data.parquet"

df = preprocess_utils.load_data(PROCESSED_FILE)

def retrieve_relevant_rows(question, df, max_rows=5):
    noise_words = {'what', 'the', 'is', 'in', 'of', 'at'}

    # keywords = question.lower().split()
    keywords = [kw for kw in question.lower().split() if kw not in noise_words]
    mask = pd.Series(False, index=df.index)

    for kw in keywords:
        if kw not in noise_words:
            mask |= df["search_text"].str.contains(kw, na=False)

    scores = df["search_text"].apply(lambda text: sum(kw in text for kw in keywords))

    return (
        df.assign(score=scores)
          .query("score > 0")
          .sort_values("score", ascending=False)
          .head(max_rows)
    )

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
        rows = retrieve_relevant_rows(prompt, df)
        
        context = rows.to_string(index=False)

        llm_prompt = f"""
        You are a real estate chatbot helping a user with property related questions.

        You will answer the user's questions using the dataset provided, performing data analysis on it to output data summaries. Do not speak in any jargon, instead present the findings in a simple manner, outputting only the relevant information to the user.

        DATA:
        {context}

        QUESTION:
        {prompt}
        """

        result = ollama.chat(
            model="qwen2.5:7b-instruct-q4_K_M",
            messages=[{"role": "user", "content": llm_prompt}]
        )

        st.write(stream_data(result["message"]["content"]))