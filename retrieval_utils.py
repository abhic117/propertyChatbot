import pandas as pd

# Checks each word within the prompt and chooses a retrieval method based on the intent
def detect_intent(question):
    noise_words = {'what', 'the', 'is', 'in', 'of', 'at'}

    price_words = {'average', 'median', 'cheap', 'cheapest', 'expensive', 'price', 'cost'}
    amenity_words = {'amenity', 'amenities', 'nearby', 'school', 'schools'}

    keywords = [kw for kw in question.lower().split() if kw not in noise_words]

    price_count = sum(1 for item in keywords if item in price_words)
    amenity_count = sum(1 for item in keywords if item in amenity_words)

    return 'price' if price_count > amenity_count else 'amenity'

# Retrieval method suited for price analysis
def price_query_retrieval(question, df, max_rows=20):
    noise_words = {'what', 'the', 'is', 'in', 'of', 'at'}

    keywords = [kw for kw in question.lower().split() if kw not in noise_words]

    scores = df["search_text"].apply(lambda text: sum(kw in text for kw in keywords))

    return (
        df.assign(score=scores)
          .query("score > 0")
          .sort_values("score", ascending=False)
          .head(max_rows)
    )
    return df.head(max_rows)

# Retrieval method suited for amenity searches
def amenity_query_retrieval(question, df, max_rows=1):
    noise_words = {'what', 'the', 'is', 'in', 'of', 'at'}

    keywords = [kw for kw in question.lower().split() if kw not in noise_words]

    # Sort df by relevancy to prompt, then keep the first 50 rows
    scores = df["search_text"].apply(lambda text: sum(kw in text for kw in keywords))
    df = df.assign(score=scores).query("score > 0").sort_values("score", ascending=False).head(20)

    # Sort df by postcode frequency, then keep first row
    df = df.sort_values("post_code", key=lambda x: x.map(x.value_counts()), ascending=False).head(max_rows)

    

    return df





