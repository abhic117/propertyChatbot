import pandas as pd

import osm_utils

def detect_intent(question):
    noise_words = {'what', 'the', 'is', 'in', 'of', 'at'}

    price_words = {'average', 'median', 'cheap', 'cheapest', 'expensive', 'price', 'cost'}
    amenity_words = {'amenity', 'amenities', 'nearby', 'school', 'schools'}

    keywords = [kw for kw in question.lower().split() if kw not in noise_words]

    price_count = sum(1 for item in keywords if item in price_words)
    amenity_count = sum(1 for item in keywords if item in amenity_words)

    return 'price' if price_count > amenity_count else 'amenity'

def price_query_retrieval(question, df, max_rows=20):
    noise_words = {'what', 'the', 'is', 'in', 'of', 'at'}

    # keywords = question.lower().split()
    keywords = [kw for kw in question.lower().split() if kw not in noise_words]
    # mask = pd.Series(False, index=df.index)

    # for kw in keywords:
    #     if kw not in noise_words:
    #         mask |= df["search_text"].str.contains(kw, na=False)

    scores = df["search_text"].apply(lambda text: sum(kw in text for kw in keywords))

    return (
        df.assign(score=scores)
          .query("score > 0")
          .sort_values("score", ascending=False)
          .head(max_rows)
    )

def amenity_query_retrieval(question, df, max_rows=3):
    noise_words = {'what', 'the', 'is', 'in', 'of', 'at'}

    keywords = [kw for kw in question.lower().split() if kw not in noise_words]

    #df['amenity_score'] = df.apply(lambda row: osm_utils.get_amenity_score(row['address'], row['post_code']), axis=1)

    scores = df["search_text"].apply(lambda text: sum(kw in text for kw in keywords))


    df = df.assign(score=scores).query("score > 0").sort_values("score", ascending=False).head(max_rows)

    df['amenity_score'] = df.apply(lambda row: osm_utils.get_amenity_score(row['address'], row['post_code']), axis=1)

    return df





