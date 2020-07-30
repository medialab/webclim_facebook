import pandas as pd
import ural

import os
import sys


def import_data(DATE):

    url_path = os.path.join(".", "data_sciencefeedback", "Appearances-Grid view " + DATE + ".csv")
    url_df = pd.read_csv(url_path)

    return url_df


def keep_only_the_urls_considered_fake_by_facebook(url_df):

    url_df = url_df[url_df['Flag as']=='False']

    url_df = url_df[url_df['Fb flagged']=="done"]

    url_df = url_df[~(url_df['Fb correction status'].isin([
        "Corrected to Not Rated",
        "Corrected to True",
        "Corrected to Partly False"
    ]))]

    return url_df


def clean_url_format(url_df):

    url_df['url_cleaned'] = url_df['url'].transform(lambda x: x.strip())

    url_df['url_cleaned'] = url_df['url_cleaned']\
        .apply(lambda x: ural.normalize_url(x, 
                                            strip_protocol=False, 
                                            strip_trailing_slash=True))
    url_df['domain_name'] = url_df['url_cleaned'].apply(lambda x: ural.get_domain_name(x))

    # Remove the URLs that are in double in the dataframe, 
    # keeping only the first, i.e. the more recent ocurrence.
    url_df = url_df.drop_duplicates(subset = "url", keep = "first")
    
    return url_df


def keep_only_field_url(url_df, TOPIC):

    fact_check_path = os.path.join(".", "data_sciencefeedback", "Reviews _ Fact-checks-Grid view " + DATE + ".csv")
    fact_check_df = pd.read_csv(fact_check_path)

    fact_check_df['field'] = fact_check_df['Review url'].str.extract('https://([^/]+)feedback.org')

    url_df = url_df.dropna(subset=['Item reviewed'])
    fact_check_df = fact_check_df.dropna(subset=['Items reviewed'])

    url_df = url_df.merge(fact_check_df[['Items reviewed', 'topic', 'field', 'Date of publication']], 
                        left_on='Item reviewed', right_on='Items reviewed', how='left')

    if TOPIC=="covid":
        url_df = url_df[(url_df['topic'].isin(["COVID-19", "COVID-19,5G"]))]
    else:
        url_df = url_df[url_df['field'] == TOPIC]

    url_df = url_df.dropna(subset=['Date of publication'])

    return url_df
 

def save_data(url_df, DATE, TOPIC):

    url_df = url_df[['url', 'url_cleaned', 'domain_name', 'Item reviewed', 'Date of publication']]

    clean_url_path = os.path.join(".", "data_sciencefeedback", "appearances_" + DATE + "_" + TOPIC + ".csv")
    url_df.to_csv(clean_url_path, index=False)

    print("The '{}' file with {} fake news url has been saved in the '{}' folder."\
        .format(clean_url_path.split('/')[-1], len(url_df), clean_url_path.split('/')[-2]))


if __name__ == "__main__":

    DATE = sys.argv[1]
    TOPIC = sys.argv[2]

    url_df = import_data(DATE)
    url_df = keep_only_the_urls_considered_fake_by_facebook(url_df)
    url_df = clean_url_format(url_df)
    url_df = keep_only_field_url(url_df, TOPIC)
    save_data(url_df, DATE, TOPIC)
