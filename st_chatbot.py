import streamlit as st
import ollama
import time
import pandas as pd
import kaggle

# kaggle.api.authenticate()
# kaggle.api.dataset_download_files(
#     'josephcheng123456/nsw-australia-property-data',
#     path='.',
#     unzip=True
# )

def load_data():
    return pd.read_csv("nsw_property_data.csv")

@st.cache_data
def prepare_dataframe(df):
    df = df.copy()
    df["search_text"] = (
        df["purchase_price"].astype(str) + " " +
        df["address"].astype(str)
    ).str.lower()
    return df

df = prepare_dataframe(load_data())

def retrieve_relevant_rows(question, df, max_rows=3):
    # keywords = question.lower().split()
    
    # mask = df.apply(
    #     lambda row: any(
    #         kw in " ".join(row.astype(str)).lower() for kw in keywords
    #     ),
    #     axis=1
    # )

    # results = df[mask].head(max_rows)
    # return results
    keywords = question.lower().split()
    mask = pd.Series(False, index=df.index)

    for kw in keywords:
        mask |= df["search_text"].str.contains(kw, na=False)

    return df.loc[mask].head(max_rows)

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

        rows = rows[['purchase_price','council_name', 'address']] \
                   .rename(columns={
                       'purchase_price': 'Price',
                       'council_name': 'Council',
                       'address': 'Address'
                   })
        
        context = rows.to_string(index=False)

        llm_prompt = f"""
        You are a data assistant.

        Answer ONLY using the dataset below.
        If the answer is not in the dataset, say you cannot find it.

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