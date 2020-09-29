import os
import warnings

import pandas as pd
import numpy as np
import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from clean_sciencefeedback_data import keep_only_the_urls_considered_fake_by_facebook, clean_url_format


warnings.filterwarnings("ignore")
pd.options.display.max_colwidth = 300


def import_data(folder, file_name):
    data_path = os.path.join(".", folder, file_name)
    df = pd.read_csv(data_path)
    return df


def keep_only_one_year_data(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] < np.max(df['date'])]
    df = df[df['date'] > np.max(df['date']) - datetime.timedelta(days=366)]
    return df


def clean_comparison_data(before_date, after_date):

    df_before = list()
    df_before.append(import_data(folder="comparison_data", file_name="fake_posts_climate_" + before_date + ".csv"))
    df_before.append(import_data(folder="comparison_data", file_name="fake_posts_health_" + before_date + ".csv"))
    df_before.append(import_data(folder="comparison_data", file_name="fake_posts_COVID-19_" + before_date + ".csv"))
    df_before = pd.concat(df_before)

    df_before = keep_only_one_year_data(df_before)

    url_df = import_data(folder="comparison_data", file_name="Appearances-Grid view " + before_date + ".csv")
    url_df = keep_only_the_urls_considered_fake_by_facebook(url_df)
    url_df = clean_url_format(url_df)

    df_before = df_before[df_before['url'].isin(url_df.url_cleaned.unique().tolist())]

    df_after = import_data(folder="data_crowdtangle_url", file_name="posts_url_" + after_date + "_.csv")
    df_after = keep_only_one_year_data(df_after)

    return df_before, df_after


def filter_accounts_sharing_less_than_x_fake_news(df, x):
    value_count = df.drop_duplicates(subset=['account_id', 'url'], keep='first')['account_id'].value_counts()
    df_filtered = df[df['account_id'].isin(value_count[value_count >= x].index)]
    return df_filtered


def print_table_1(df_before, df_after):

    df_before_filtered = filter_accounts_sharing_less_than_x_fake_news(df_before, x=10)
    print('\nThere are {} Facebook accounts sharing more than 10 fake news in the June data.'\
        .format(df_before_filtered.account_id.nunique()))


    list_qanon_before = [name for name in list(df_before_filtered.account_name.value_counts().index) if 'Q' in name]
    print('The list of the {} QAnon related accounts in the June data:'.format(len(list_qanon_before)))
    print(*list_qanon_before, sep='\n')

    df_after_filtered = filter_accounts_sharing_less_than_x_fake_news(df_after, x=10)
    print('\nThere are {} Facebook accounts sharing more than 10 fake news in the August data.'\
        .format(df_after_filtered.account_id.nunique()))
    list_qanon_after = [name for name in list(df_after_filtered.account_name.value_counts().index) if 'Q' in name]
    print('The list of the {} QAnon related accounts in the Augsut data:'.format(len(list_qanon_after)))
    print(*list_qanon_after, sep='\n')


def save_figure(figure_name):

    figure_path = os.path.join('.', 'figure_web_conference', figure_name + '.png')
    plt.savefig(figure_path)

    print('\n\n' + figure_name.upper())
    print("The '{}' figure has been saved in the '{}' folder."\
        .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


def clean_crowdtangle_group_data(suffix):

    posts_group_df = import_data(folder="data_crowdtangle_group", 
                                 file_name="posts_" + suffix + "_group.csv")
    print('\nThere are {} Facebook groups about {}.'.format(posts_group_df.account_id.nunique(), suffix))

    posts_page_df = import_data(folder="data_crowdtangle_group", 
                                file_name="posts_" + suffix + "_page.csv")
    print('There are {} Facebook pages about {}.'.format(posts_page_df.account_id.nunique(), suffix))

    posts_df = pd.concat([posts_group_df, posts_page_df])

    posts_df['date'] = pd.to_datetime(posts_df['date'])
    posts_df = posts_df[posts_df['date'] < datetime.datetime.strptime(DATE, '%Y-%m-%d')]

    return posts_df


def details_temporal_evolution(posts_df, plot_special_date):

    if plot_special_date:
        plt.axvline(x=np.datetime64("2020-06-09"), color='black', linestyle='--', linewidth=1)

    plt.legend()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    if (datetime.datetime.strptime(DATE, '%Y-%m-%d') - 
        datetime.datetime.strptime(np.min(posts_df["date"]).strftime("%Y-%m-%d"), '%Y-%m-%d')).days < 365:
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2)) 
    else:
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=4))

    plt.xlim(
        np.datetime64(datetime.datetime.strptime(np.min(posts_df["date"]).strftime("%Y-%m-%d"), '%Y-%m-%d') -
                      datetime.timedelta(days=4)), 
        np.datetime64(datetime.datetime.strptime(DATE, '%Y-%m-%d') + datetime.timedelta(days=4))
    )
    plt.ylim(bottom=0)


def plot_all_groups(posts_df, title_detail, plot_special_date=True):

    plt.figure(figsize=(10, 8))
    plt.subplot(211)

    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of reactions per day")

    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of shares per day")

    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of comments per day")

    details_temporal_evolution(posts_df, plot_special_date)
    plt.title("The temporal evolution of the {} Facebook accounts ".format(posts_df["account_id"].nunique()) + title_detail)

    plt.subplot(212)

    plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
        label="Mean number of posts per day", color="grey")

    details_temporal_evolution(posts_df, plot_special_date)

    plt.tight_layout()


def save_figure_3(posts_df):

    plot_all_groups(posts_df, title_detail="spreading misinformation")
    save_figure('figure_3')


def save_figure_4(posts_df):

    list_complete_groups_id = []
    for id in posts_df['account_id'].unique():
        posts_df_group = posts_df[posts_df["account_id"] == id]
        if ((np.min(posts_df_group['date']) == np.min(posts_df['date'])) & 
            (np.max(posts_df_group['date']) == datetime.datetime.strptime(DATE, '%Y-%m-%d') - datetime.timedelta(days=1))):
            list_complete_groups_id.append(id)
    posts_df_temp = posts_df[posts_df["account_id"].isin(list_complete_groups_id)]

    plot_all_groups(posts_df_temp, title_detail="spreading misinformation")

    save_figure('figure_4')


def save_figure_5(posts_df):

    plot_all_groups(posts_df, title_detail="spreading main news")
    save_figure('figure_5')


if __name__ == "__main__":

    DATE = "2020-08-27"

    df_before, df_after = clean_comparison_data(before_date="02_06_2020", after_date="2020-08-31")
    print_table_1(df_before, df_after)

    posts_fake_df = clean_crowdtangle_group_data("fake_news")
    save_figure_3(posts_fake_df)
    save_figure_4(posts_fake_df)

    posts_main_df = clean_crowdtangle_group_data("main_news")
    save_figure_5(posts_main_df)
