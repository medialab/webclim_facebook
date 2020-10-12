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
    
    print('\n\nTABLE 1')

    df_before_filtered = filter_accounts_sharing_less_than_x_fake_news(df_before, x=10)
    print('\nThere are {} Facebook accounts sharing more than 10 fake news in the June data.'\
        .format(df_before_filtered.account_id.nunique()))

    list_qanon_before = [name for name in list(df_before_filtered.account_name.value_counts().index) if 'Q' in name]
    print('The list of the {} QAnon related accounts in the June data:'.format(len(list_qanon_before)))
    print(df_before_filtered[df_before_filtered['account_name'].isin(list_qanon_before)]\
        [['account_name', 'account_subscriber_count']].drop_duplicates()\
        .sort_values(by='account_subscriber_count', ascending=False).to_string(index=False))
    print('Total number of follower: {}'.format(np.sum(df_before_filtered[df_before_filtered['account_name'].isin(list_qanon_before)]\
        [['account_name', 'account_subscriber_count']].drop_duplicates()[['account_subscriber_count']].values)))


    df_after_filtered = filter_accounts_sharing_less_than_x_fake_news(df_after, x=10)
    print('\nThere are {} Facebook accounts sharing more than 10 fake news in the August data.'\
        .format(df_after_filtered.account_id.nunique()))

    list_qanon_after = [name for name in list(df_after_filtered.account_name.value_counts().index) if 'Q' in name]
    print('The list of the {} QAnon related accounts in the Augsut data:'.format(len(list_qanon_after)))
    print(df_after_filtered[df_after_filtered['account_name'].isin(list_qanon_after)]\
        [['account_name', 'account_subscriber_count']].drop_duplicates()\
        .sort_values(by='account_subscriber_count', ascending=False).to_string(index=False))
    print('Total number of follower: {}'.format(np.sum(df_after_filtered[df_after_filtered['account_name'].isin(list_qanon_after)]\
        [['account_name', 'account_subscriber_count']].drop_duplicates()[['account_subscriber_count']].values)))


def print_table_2(df_before, df_after):

    print('\n\nTABLE 2')

    df_before_filtered = filter_accounts_sharing_less_than_x_fake_news(df_before, x=3)
    print('\nThere are {} Facebook accounts sharing more than 3 fake news in the June data.'\
        .format(df_before_filtered.account_id.nunique()))

    list_qanon_before = [name for name in list(df_before_filtered.account_name.value_counts().index) if 'Q' in name]
    accounts_to_remove_before = [
        "Vương Nhất Bác 王一博 - UNIQ's Wang Yibo 1st Vietnamese Fanpage",
        'QUESTION EVERYTHING... EVERYWHERE',
        'QuantumEquilibrium ~ The Truth State',
        '@STOP 5 G MONTRÉAL/QUÉBEC',
        'AMERICANS Against Excessive Quarantine!',
        'Questioning Global Warming',
        'QUESTION EVERYTHING',
        'Rastos Quimicos Portugal//Chemtrail Activism',
        'Natural And Quodesh',
        'STOP 5G Val-David. Laurentides et autres circonscriptions du Québec',
        'Rockcastle County C.V.Q.R.G',
        'Info Pro-Trump  Québec'
    ]
    list_qanon_before = [x for x in list_qanon_before if x not in accounts_to_remove_before]

    print('There are {} accounts with Q in their names in the June data.'.format(len(list_qanon_before)))
    print('Total number of follower: {}'.format(np.sum(df_before_filtered[df_before_filtered['account_name'].isin(list_qanon_before)]\
        [['account_name', 'account_subscriber_count']].drop_duplicates()[['account_subscriber_count']].values)))


    df_after_filtered = filter_accounts_sharing_less_than_x_fake_news(df_after, x=3)
    print('\nThere are {} Facebook accounts sharing more than 3 fake news in the August data.'\
        .format(df_after_filtered.account_id.nunique()))

    list_qanon_after = [name for name in list(df_after_filtered.account_name.value_counts().index) if 'Q' in name]
    accounts_to_remove_after = [
        'QUESTION EVERYTHING... EVERYWHERE',
        'AMERICANS Against Excessive Quarantine!',
        'Info Pro-Trump  Québec',
        'Médias Alternatifs Québecois',
        'Wisconsinites Against Excessive Quarantine',
        'Minnesotans Against Excessive Quarantine',
        'Venner, der synes godt om Question Everything',
        'Spiritual Awakening, Quantum Physics, Aliens & The 5th Dimension',
        'Canadians Against Excessive Quarantine',
        'PRQBUĐENI HRVATSKA',
        'Quotes of Life',
        'QUESTION EVERYTHING',
        'Rastos Quimicos Portugal//Chemtrail Activism',
        '@STOP 5 G MONTRÉAL/QUÉBEC',
        'QuantumEquilibrium ~ The Truth State',
        'STOP 5G Val-David. Laurentides et autres circonscriptions du Québec',
        'Rockcastle County C.V.Q.R.G'
    ]
    list_qanon_after = [x for x in list_qanon_after if x not in accounts_to_remove_after]

    print('There are {} accounts with Q in their names in the August data.'.format(len(list_qanon_after)))
    print('Total number of follower: {}'.format(np.sum(df_after_filtered[df_after_filtered['account_name'].isin(list_qanon_after)]\
        [['account_name', 'account_subscriber_count']].drop_duplicates()[['account_subscriber_count']].values)))


def clean_crowdtangle_url_data(post_url_df, url_df):

    post_url_df = post_url_df[post_url_df["platform"] == "Facebook"]
    post_url_df = post_url_df.dropna(subset=['account_id', 'url'])

    post_url_df = post_url_df.sort_values(by=['datetime'], ascending=True)
    post_url_df = post_url_df.drop_duplicates(subset=['account_id', 'url'], keep='first')

    post_url_df = post_url_df[['url', 'account_id', 'account_name', 'account_subscriber_count', 'date']]

    post_url_df = post_url_df.merge(url_df[['url', 'scientific_topic']], on='url', how='left')

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


def details_temporal_evolution(posts_df, plot_special_date):

    if plot_special_date:
        plt.axvline(x=np.datetime64("2020-06-09"), color='black', linestyle='--', linewidth=1)

    plt.legend()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))

    plt.xlim(
        np.datetime64(datetime.datetime.strptime('2019-09-01', '%Y-%m-%d') - datetime.timedelta(days=4)), 
        np.datetime64(datetime.datetime.strptime('2020-08-31', '%Y-%m-%d') + datetime.timedelta(days=4))
    )
    plt.ylim(bottom=0)


def plot_one_group(posts_df, account_id, plot_special_date):
    
    posts_df_group = posts_df[posts_df["account_id"] == account_id]
    
    plt.plot(posts_df_group.groupby(by=["date"])["reaction"].mean(), 
            label="Mean number of reactions per post")

    plt.plot(posts_df_group.groupby(by=["date"])["comment"].mean(), 
            label="Mean number of comments per post")
    
    details_temporal_evolution(posts_df, plot_special_date)


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


def compute_repeat_offender_periods(fake_news_dates):

    repeat_offender_periods = []

    if len(fake_news_dates) > 1:
        for index in range(1, len(fake_news_dates)):
            if fake_news_dates[index] - fake_news_dates[index - 1] < np.timedelta64(90, 'D'):

                repeat_offender_periods.append([
                    fake_news_dates[index],
                    fake_news_dates[index - 1] + np.timedelta64(90, 'D')
                ])

    return repeat_offender_periods


def merge_overlapping_periods(overlapping_periods):
    
    if len(overlapping_periods) == 0:
        return []
    
    else:
        overlapping_periods.sort(key=lambda interval: interval[0])
        merged_periods = [overlapping_periods[0]]

        for current in overlapping_periods:
            previous = merged_periods[-1]
            if current[0] <= previous[1]:
                previous[1] = max(previous[1], current[1])
            else:
                merged_periods.append(current)

        return merged_periods


def save_figure(figure_name):

    figure_path = os.path.join('.', 'figure_web_conference', figure_name + '.png')
    plt.savefig(figure_path)

    print('\n\n' + figure_name.upper())
    print("The '{}' figure has been saved in the '{}' folder."\
        .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


def save_figure_1(posts_df, post_url_df, url_df, plot_repeat_offender_periods=False):

    accounts_to_plot = [
        'Humanity vs Insanity - The CRANE Report',
        'Vaccination Information Network - UK (VINE UK)',
        'Exposing The New World Order',
        'People Concerned About Corruption in Our Government'
    ]

    plt.figure(figsize=(12, 5))

    for group_index in range(4):
        account_id = posts_df[posts_df['account_name']==accounts_to_plot[group_index]].account_id.unique()[0]

        ax = plt.subplot(2, 2, group_index + 1)

        fake_news_dates = compute_fake_news_dates(post_url_df, url_df, account_id)
        for date in fake_news_dates:
            plt.axvline(x=date, color='C7', linestyle='-')

        if plot_repeat_offender_periods:
            repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
            repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)
            for period in repeat_offender_periods:
                plt.axvspan(period[0], period[1], facecolor='r', alpha=0.2)

        plot_one_group(posts_df, account_id, plot_special_date=False)
        
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

    plt.tight_layout()
    save_figure('figure_1')


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


def print_drop_percentages(posts_df):
    print('\nFor the {} Facebook accounts about fake news:'.format(posts_df.account_id.nunique()))

    for metric in ['reaction', 'share', 'comment']:
        serie = posts_df.groupby(by=["date"])[metric].sum()/posts_df.groupby(by=["date"])["account_id"].nunique()
        print('The ' + metric +'s have dropped by {}% between June 8 and 10, 2020.'.format(
            int(np.around((serie.loc['2020-06-08'] - serie.loc['2020-06-10']) * 100 / serie.loc['2020-06-08'], decimals=0))
        ))


def print_figure_3_statistics(posts_df):

    print_drop_percentages(posts_df)

    list_complete_groups_id = []
    for id in posts_df['account_id'].unique():
        posts_df_group = posts_df[posts_df["account_id"] == id]
        if ((np.min(posts_df_group['date']) == np.min(posts_df['date'])) & 
            (np.max(posts_df_group['date']) == np.max(posts_df['date']))):
            list_complete_groups_id.append(id)
    posts_df_temp = posts_df[posts_df["account_id"].isin(list_complete_groups_id)]

    print_drop_percentages(posts_df_temp)


def save_figure_4(posts_df):

    plot_all_groups(posts_df, title_detail="spreading main news")
    save_figure('figure_4')


if __name__ == "__main__":

    DATE = "2020-08-27"
    DATE_URL_REQUEST = "2020-08-31"

    df_before, df_after = clean_comparison_data(before_date="02_06_2020", after_date="2020-08-31")
    print_table_1(df_before, df_after)
    print_table_2(df_before, df_after)

    url_df = import_data(folder="data_sciencefeedback", file_name="appearances_" + DATE + "_.csv")

    post_url_df = import_data(folder="data_crowdtangle_url", file_name="posts_url_" + DATE_URL_REQUEST + "_.csv")
    post_url_df = clean_crowdtangle_url_data(post_url_df, url_df)

    posts_fake_df = clean_crowdtangle_group_data("fake_news")
    posts_offenders_df = clean_crowdtangle_group_data("repeat_offenders")
    posts_groups_df = pd.concat([posts_fake_df, posts_offenders_df])

    save_figure_1(posts_groups_df, post_url_df, url_df, plot_repeat_offender_periods=False)

    save_figure_3(posts_fake_df)
    print_figure_3_statistics(posts_fake_df)

    posts_main_df = clean_crowdtangle_group_data("main_news")
    save_figure_4(posts_main_df)
