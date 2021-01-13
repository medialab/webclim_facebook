import os
import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def import_data(folder, file_name):
    data_path = os.path.join(".", "data", folder, file_name)
    df = pd.read_csv(data_path)
    return df


def export_data(df, folder, file_name):
    csv_path = os.path.join('.', 'data', folder, file_name)
    df.to_csv(csv_path, index=False)
    print("The '{}' file has been printed in the '{}' folder".format(
        csv_path.split('/')[-1], csv_path.split('/')[-2])
    )


def save_figure(figure_name, folder=None, dpi=None):

    if folder:
        figure_path = os.path.join('.', 'figure', folder, figure_name + '.png')
    else:
        figure_path = os.path.join('.', 'figure', figure_name + '.png')
    
    plt.savefig(figure_path, dpi=dpi)

    print('\n\n' + figure_name.upper())
    print("The '{}' figure has been saved in the '{}' folder."\
        .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


def keep_only_one_year_data(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] < np.max(df['date'])]
    df = df[df['date'] > np.max(df['date']) - datetime.timedelta(days=366)]
    return df


def clean_crowdtangle_url_data(post_url_df):

    post_url_df = post_url_df[post_url_df["platform"] == "Facebook"]
    post_url_df = post_url_df.dropna(subset=['account_id', 'url'])

    post_url_df = post_url_df.sort_values(by=['datetime'], ascending=True)
    post_url_df = post_url_df.drop_duplicates(subset=['account_id', 'url'], keep='first')
    post_url_df['account_id'] = post_url_df['account_id'].astype(int)

    post_url_df = post_url_df[['url', 'account_id', 'account_name', 'account_subscriber_count', 'date']]

    return post_url_df
