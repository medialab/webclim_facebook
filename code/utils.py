import os
import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def import_data(folder, file_name):
    data_path = os.path.join(".", "data", folder, file_name)
    df = pd.read_csv(data_path)
    return df


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

    post_url_df = post_url_df[['url', 'account_id', 'account_name', 'account_subscriber_count', 'date']]

    return post_url_df


def clean_crowdtangle_group_data(suffix):

    posts_group_df = import_data(folder="data_crowdtangle_group", 
                                 file_name="posts_" + suffix + "_group.csv")
    print('\nThere are {} Facebook groups about {}.'.format(posts_group_df.account_id.nunique(), suffix))

    posts_page_df = import_data(folder="data_crowdtangle_group", 
                                file_name="posts_" + suffix + "_page.csv")
    print('There are {} Facebook pages about {}.'.format(posts_page_df.account_id.nunique(), suffix))

    posts_df = pd.concat([posts_group_df, posts_page_df])

    posts_df['date'] = pd.to_datetime(posts_df['date'])
    posts_df = posts_df[posts_df['date'] >= datetime.datetime.strptime('2019-09-01', '%Y-%m-%d')]
    posts_df = posts_df[posts_df['date'] <= datetime.datetime.strptime('2020-08-31', '%Y-%m-%d')]

    return posts_df