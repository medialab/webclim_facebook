"""This script is used to clean and gather data 
from the two CSV files extracted from the Science Feedback AirTable"""

import pandas as pd
import ural
import time

import os
import sys


def import_data(RAW_DATA_DIRECTORY, DATE):
    """Import dataframe from the two csv extracted from the 
    Science Feedback AirTable database."""

    url_path = os.path.join(".", RAW_DATA_DIRECTORY, "Appearances-Grid view " + DATE + ".csv")
    url_df = pd.read_csv(url_path)

    fact_check_path = os.path.join(".", RAW_DATA_DIRECTORY, "Reviews _ Fact-checks-Grid view " + DATE + ".csv")
    fact_check_df = pd.read_csv(fact_check_path)

    return url_df, fact_check_df


def keep_only_fake_url(url_df):
    url_df = url_df[(url_df['Flag as'].isin(['False', 'Partly false', 'Misleading', 'False headline']))]
    return url_df


def keep_only_one_topic(url_df, fact_check_df, SCIENTIFIC_TOPIC):

    # Use a REGEX to get the article field from the fact-check url website:
    # if the fact-check url starts with 'https://climatefeedback.org' -> 'climate' article
    # if the fact-check url starts with 'https://healthfeedback.org'  -> 'health' article
    fact_check_df['field'] = fact_check_df['Review url'].str.extract('https://([^/]+)feedback.org')

    # Merge the two dataframes to get the 'field' for each url:
    url_df = url_df.dropna(subset=['Item reviewed'])
    fact_check_df = fact_check_df.dropna(subset=['Items reviewed'])
    url_df = url_df.merge(fact_check_df[['Items reviewed', 'field', 'topic']], 
                        left_on='Item reviewed', right_on='Items reviewed', how='left')

    # Keep only the URL about the scientific topic of interest:
    url_df.loc[url_df['topic'] == 'COVID-19', 'field'] = 'COVID-19'
    url_df = url_df.dropna(subset=['field'])
    url_df = url_df[url_df['field'] == SCIENTIFIC_TOPIC]

    return url_df


def clean_url(url_df):
    """Clean and merge the appearance data"""

    # Remove the spaces added by error arount the URLs
    url_df['url'] = url_df['url'].transform(lambda x: x.strip())

    # Clean the URLs and extract its domain name:
    url_df['url'] = url_df['url'].apply(lambda x: ural.normalize_url(x, 
                                                                     strip_protocol=False, 
                                                                     strip_trailing_slash=True))
    url_df['domain_name'] = url_df['url'].apply(lambda x: ural.get_domain_name(x))

    # Remove the URLs that are in double in the dataframe, 
    # keeping only the first, i.e. the more recent ocurrence.
    url_df = url_df.drop_duplicates(subset = "url", keep = "first")

    # # Remove the plateforms from the analysis:
    # plateforms = ["facebook.com", "youtube.com", "twitter.com", "wordpress.com", "instagram.com"]
    # url_df = url_df[~url_df['domain_name'].isin(plateforms)]

    # # Remove the url with parameters from the analysis because CT return wrong results for them:
    # url_df['parameter_in_url'] = url_df['url'].apply(lambda x: '?' in x)
    # url_df = url_df[url_df['parameter_in_url']==False]
    
    return url_df
    

def save_data(url_df, SCIENTIFIC_TOPIC, CLEAN_DATA_DIRECTORY, DATE):
    url_df = url_df[['url', 'Item reviewed', 'field', 'domain_name']]

    clean_url_path = os.path.join(".", CLEAN_DATA_DIRECTORY, 
                                  "fake_url_" + SCIENTIFIC_TOPIC + "_" + DATE + ".csv")
    url_df.to_csv(clean_url_path, index=False)
    print("The 'fake_url_{}_{}.csv' file has been saved in the 'clean_data' folder.".format(SCIENTIFIC_TOPIC, DATE))


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        if sys.argv[1] in ["COVID-19", "health", "climate"]:
            SCIENTIFIC_TOPIC = sys.argv[1]
        else:
            print("Please enter only 'COVID-19', 'health' or 'climate' as argument.")
            exit()
    else:
        SCIENTIFIC_TOPIC = "COVID-19"
        print("The topic 'COVID-19' has been chosen by default.")

    if len(sys.argv) >= 3:
        DATE = sys.argv[2]
    else:
        DATE = "02_06_2020"
        print("The date '{}' has been chosen by default.".format(DATE))

    RAW_DATA_DIRECTORY = "raw_data"
    CLEAN_DATA_DIRECTORY = "clean_data"

    url_df, fact_check_df = import_data(RAW_DATA_DIRECTORY, DATE)
    url_df = keep_only_fake_url(url_df)
    url_df = keep_only_one_topic(url_df, fact_check_df, SCIENTIFIC_TOPIC)
    url_df = clean_url(url_df)
    save_data(url_df, SCIENTIFIC_TOPIC, CLEAN_DATA_DIRECTORY, DATE)
    
