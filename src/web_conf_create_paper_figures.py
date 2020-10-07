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


def clean_crowdtangle_url_data(post_url_df, url_df):

    post_url_df = post_url_df[post_url_df["platform"] == "Facebook"]
    post_url_df = post_url_df.dropna(subset=['account_id', 'url'])

    post_url_df = post_url_df.sort_values(by=['datetime'], ascending=True)
    post_url_df = post_url_df.drop_duplicates(subset=['account_id', 'url'], keep='first')

    post_url_df = post_url_df[['url', 'account_id', 'account_name', 'account_subscriber_count', 'date']]

    post_url_df = post_url_df.merge(url_df[['url', 'scientific_topic']], on='url', how='left')

    return post_url_df


def clean_crowdtangle_group_data(suffix, DATE):

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


def details_temporal_evolution(posts_df, plot_special_date, DATE):

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


def plot_one_group(posts_df, account_id, plot_special_date, DATE):
    
    posts_df_group = posts_df[posts_df["account_id"] == account_id]
    
    plt.plot(posts_df_group.groupby(by=["date"])["reaction"].mean(), 
            label="Mean number of reactions per post")

    plt.plot(posts_df_group.groupby(by=["date"])["comment"].mean(), 
            label="Mean number of comments per post")
    
    details_temporal_evolution(posts_df, plot_special_date, DATE)


def compute_fake_news_dates(post_url_df, url_df, account_id):

    post_url_group_df = post_url_df[post_url_df["account_id"]==account_id]
    urls = post_url_group_df["url"].unique().tolist()

    fake_news_dates = []

    for url in urls:
        potential_dates = []

        # We consider the date of the Facebook post or posts:
        potential_dates.append(post_url_group_df[post_url_group_df["url"] == url]["date"].values[0])
        # We consider the date of the fact-check:
        potential_dates.append(url_df[url_df['url']==url]["Date of publication"].values[0])
        # TODO: We need to add the date coming from the 'data_sciencefeedback/Rated Archive (06-01-2020 to 07-02-2020).csv' file

        potential_dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in potential_dates]
        date_to_plot = np.datetime64(np.max(potential_dates))

        plt.axvline(x=date_to_plot, color='black')
        fake_news_dates.append(date_to_plot)
        
    fake_news_dates.sort()

    return fake_news_dates


def save_figure(figure_name):

    figure_path = os.path.join('.', 'figure_web_conference', figure_name + '.png')
    plt.savefig(figure_path)

    print('\n\n' + figure_name.upper())
    print("The '{}' figure has been saved in the '{}' folder."\
        .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


def save_figure_1(posts_df, post_url_df, url_df, DATE):

    accounts_to_plot = [
        'Humanity vs Insanity - The CRANE Report',
        'Vaccination Information Network - UK (VINE UK)',
        'Exposing The New World Order',
        'People Concerned About Corruption in Our Government'
    ]

    plt.figure(figsize=(12, 5))

    for group_index in range(4):
        account_id = posts_groups_df[posts_groups_df['account_name']==accounts_to_plot[group_index]].account_id.unique()[0]

        ax = plt.subplot(2, 2, group_index + 1)

        fake_news_dates = compute_fake_news_dates(post_url_df, url_df, account_id)
        for date in fake_news_dates:
            plt.axvline(x=date, color='C7', linestyle='-')

        plot_one_group(posts_groups_df, account_id, plot_special_date=False, DATE=DATE)
        
        if group_index == 0: 
            plt.ylim([0, 20])
        else:
            ax.get_legend().set_visible(False)

        if group_index == 0:
            plt.ylabel('REDUCED PERIODS\n', fontsize='large')
        elif group_index == 2:
            plt.ylabel('STABLE REACH\n', fontsize='large')

        if group_index == 0:
            plt.title('ACCOUNTS SHARING MANY MISINFORMATION LINKS\n\n' + accounts_to_plot[group_index], fontsize='large')
        elif group_index == 1:
            plt.title('ACCOUNTS SHARING FEW MISINFORMATION LINKS\n\n' + accounts_to_plot[group_index], fontsize='large')
        else:
            plt.title(accounts_to_plot[group_index], fontsize='large')


        plt.xlim(
            np.datetime64(datetime.datetime.fromisoformat('2019-09-01') - datetime.timedelta(days=4)),
            np.datetime64(datetime.datetime.strptime(DATE, '%Y-%m-%d') + datetime.timedelta(days=4))
        )

    plt.tight_layout()
    save_figure('figure_1')


def plot_all_groups(posts_df, title_detail, DATE, plot_special_date=True):

    plt.figure(figsize=(10, 8))
    plt.subplot(211)

    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of reactions per day")

    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of shares per day")

    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of comments per day")

    details_temporal_evolution(posts_df, plot_special_date, DATE)
    plt.title("The temporal evolution of the {} Facebook accounts ".format(posts_df["account_id"].nunique()) + title_detail)

    plt.subplot(212)

    plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
        label="Mean number of posts per day", color="grey")

    details_temporal_evolution(posts_df, plot_special_date, DATE)

    plt.tight_layout()


def save_figure_3(posts_df, DATE):

    plot_all_groups(posts_df, title_detail="spreading misinformation", DATE=DATE)
    save_figure('figure_3')


def save_figure_4(posts_df, DATE):

    list_complete_groups_id = []
    for id in posts_df['account_id'].unique():
        posts_df_group = posts_df[posts_df["account_id"] == id]
        if ((np.min(posts_df_group['date']) == np.min(posts_df['date'])) & 
            (np.max(posts_df_group['date']) == datetime.datetime.strptime(DATE, '%Y-%m-%d') - datetime.timedelta(days=1))):
            list_complete_groups_id.append(id)
    posts_df_temp = posts_df[posts_df["account_id"].isin(list_complete_groups_id)]

    plot_all_groups(posts_df_temp, title_detail="spreading misinformation", DATE=DATE)

    save_figure('figure_4')


def save_figure_5(posts_df, DATE):

    plot_all_groups(posts_df, title_detail="spreading main news", DATE=DATE)
    save_figure('figure_5')


if __name__ == "__main__":

    DATE = "2020-08-27"
    DATE_URL_REQUEST = "2020-08-31"

    # df_before, df_after = clean_comparison_data(before_date="02_06_2020", after_date="2020-08-31")
    # print_table_1(df_before, df_after)

    url_df = import_data(folder="data_sciencefeedback", file_name="appearances_" + DATE + "_.csv")

    post_url_df = import_data(folder="data_crowdtangle_url", file_name="posts_url_" + DATE_URL_REQUEST + "_.csv")
    post_url_df = clean_crowdtangle_url_data(post_url_df, url_df)

    posts_fake_df = clean_crowdtangle_group_data("fake_news", DATE)
    posts_offenders_df = clean_crowdtangle_group_data("repeat_offenders", DATE)
    posts_groups_df = pd.concat([posts_fake_df, posts_offenders_df])

    save_figure_1(posts_groups_df, post_url_df, url_df, DATE)

    # save_figure_3(posts_fake_df, DATE)
    # save_figure_4(posts_fake_df, DATE)

    # posts_main_df = clean_crowdtangle_group_data("main_news", DATE)
    # save_figure_5(posts_main_df, DATE)
