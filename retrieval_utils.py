import pandas as pd

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