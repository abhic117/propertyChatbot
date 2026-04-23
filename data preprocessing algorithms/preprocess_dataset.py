import kaggle
import os
import pandas as pd

RAW_FILE = "nsw_property_data.csv"
PROCESSED_FILE = "processed_nsw_property_data.parquet"

# Download dataset and extract only relevant columns into dataframe
def preprocess_data(raw_file, processed_file):
    kaggle.api.dataset_download_files(
    'josephcheng123456/nsw-australia-property-data',
    path='.',
    unzip=True
    )
    
    df = pd.read_csv(raw_file)

    df = df[df['council_name'] == 'BLACKTOWN']

    df["search_text"] = (
        df["council_name"].astype(str) + " " +
        df["purchase_price"].astype(str) + " " +
        df["address"].astype(str)
    ).str.lower()

    df = df[['council_name', 'purchase_price', 'address', 'post_code', 'search_text']]

    df.to_parquet(processed_file)

if not os.path.exists(PROCESSED_FILE):
    preprocess_data(RAW_FILE, PROCESSED_FILE)