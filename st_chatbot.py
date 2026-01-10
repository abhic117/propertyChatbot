import streamlit as st
import ollama
import time
import pandas as pd
import kaggle

kaggle.api.authenticate()
kaggle.api.dataset_download_files(
    'josephcheng123456/nsw-australia-property-data',
    path='.',
    unzip=True
)

df = pd.read_csv("nsw_property_data.csv")

def retrieve_relevant_rows(question, df, max_rows=5):
    keywords = question.lower().split()
    
    mask = df.apply(
        lambda row: any(
            kw in " ".join(row.astype(str)).lower() for kw in keywords
        ),
        axis=1
    )

    results = df[mask].head(max_rows)
    return results

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
        # result = ollama.chat(model="tinyllama", messages=[{
        #     "role":"user",
        #     "content":prompt,
        # }])
        # response = result["message"]["content"]
        # st.write(stream_data(response))
        rows = retrieve_relevant_rows(prompt, df)
        context = rows.to_string(index=False)

        llm_prompt = f"""
        Use the NSW property data below to answer the question.

        DATA:
        {context}

        QUESTION:
        {prompt}
        """

        result = ollama.chat(
            model="tinyllama",
            messages=[{"role": "user", "content": llm_prompt}]
        )

        st.write(stream_data(result["message"]["content"]))