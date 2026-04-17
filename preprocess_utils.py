import kaggle
import os
import pandas as pd

# Download dataset and extract only relevant columns into dataframe
def preprocess_data(raw_file, processed_file):
    kaggle.api.dataset_download_files(
    'josephcheng123456/nsw-australia-property-data',
    path='.',
    unzip=True
    )
    
    df = pd.read_csv(raw_file)

    df["search_text"] = (
        df["council_name"].astype(str) + " " +
        df["purchase_price"].astype(str) + " " +
        df["address"].astype(str)
    ).str.lower()

    df = df[['council_name', 'purchase_price', 'address', 'post_code', 'search_text']]

    df.to_parquet(processed_file)

# Download data only if it does not already exist
def load_data(raw_file, processed_file):
    if not os.path.exists(processed_file):
        preprocess_data(raw_file, processed_file)
    return pd.read_parquet(processed_file)