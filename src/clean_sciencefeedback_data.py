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


def keep_only_covid_url(url_df):

    fact_check_path = os.path.join(".", "data_sciencefeedback", "Reviews _ Fact-checks-Grid view " + DATE + ".csv")
    fact_check_df = pd.read_csv(fact_check_path)

    url_df = url_df.dropna(subset=['Item reviewed'])
    fact_check_df = fact_check_df.dropna(subset=['Items reviewed'])

    url_df = url_df.merge(fact_check_df[['Items reviewed', 'topic', 'Date of publication']], 
                        left_on='Item reviewed', right_on='Items reviewed', how='left')

    url_df = url_df[(url_df['topic'].isin(["COVID-19", "COVID-19,5G"]))]
    url_df = url_df.dropna(subset=['Date of publication'])

    return url_df
 

def save_data(url_df, DATE):

    url_df = url_df[['url', 'url_cleaned', 'domain_name', 'Item reviewed', 'Date of publication']]
    # url_df = url_df.iloc[1:, :]
    # url_df = url_df.sample()

    clean_url_path = os.path.join(".", "data_sciencefeedback", "appearances_" + DATE + "_clean.csv")
    url_df.to_csv(clean_url_path, index=False)

    print("The clean data file with {} fake news url has been saved in the 'data_sciencefeedback' folder."\
        .format(len(url_df)))


if __name__ == "__main__":

    if len(sys.argv) >= 2:
        DATE = sys.argv[2]
    else:
        DATE = "2020-06-29"
        print("The date '{}' has been chosen by default.".format(DATE))

    url_df = import_data(DATE)
    url_df = keep_only_the_urls_considered_fake_by_facebook(url_df)
    url_df = clean_url_format(url_df)
    url_df = keep_only_covid_url(url_df)
    save_data(url_df, DATE)
