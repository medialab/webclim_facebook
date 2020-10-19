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


def save_figure(figure_name):

    figure_path = os.path.join('.', 'figure_web_conference', figure_name + '.png')
    plt.savefig(figure_path)

    print('\n\n' + figure_name.upper())
    print("The '{}' figure has been saved in the '{}' folder."\
        .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


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

def plot_all_groups(posts_df, title_detail):

    plt.figure(figsize=(8, 10))
    # plt.figure(figsize=(8, 7))

    plt.subplot(311)
    # plt.subplot(211)
    plt.title('The temporal evolution of the {} '.format(posts_df["account_id"].nunique()) + title_detail + ' Facebook accounts')

    plt.plot(posts_df.groupby(by=["date", 'account_id'])['reaction'].mean().groupby(by=['date']).mean(), 
            label="Mean number of reactions per post")

    plt.plot(posts_df.groupby(by=["date", 'account_id'])['comment'].mean().groupby(by=['date']).mean(), 
            label="Mean number of comments per post")

    plt.plot(posts_df.groupby(by=["date", 'account_id'])['share'].mean().groupby(by=['date']).mean(), 
            label="Mean number of shares per post")

    details_temporal_evolution(posts_df, plot_special_date=True)
    plt.ylim(bottom=0)

    plt.subplot(312)
    # plt.subplot(212)

    plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
        label="Mean number of posts per day", color="grey")

    details_temporal_evolution(posts_df, plot_special_date=True)
    plt.ylim(bottom=0)

    plt.subplot(313)

    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of reactions per day")

    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of comments per day")

    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of shares per day")

    details_temporal_evolution(posts_df, plot_special_date=True)
    plt.ylim(bottom=0)

    plt.tight_layout()


def save_figure_1(posts_df):

    plot_all_groups(posts_df, title_detail="misinformation")
    save_figure('figure_1')


def print_evolution_percentages(posts_df):
    print('\nFor the {} Facebook accounts about fake news:'.format(posts_df.account_id.nunique()))

    for metric in ['reaction', 'share', 'comment']:
        serie = posts_df.groupby(by=["date", 'account_id'])[metric].mean().groupby(by=['date']).mean()
        print('The ' + metric +'s has evolved by {}% between June 8 and 10, 2020.'.format(
            int(np.around((serie.loc['2020-06-10'] - serie.loc['2020-06-08']) * 100 / serie.loc['2020-06-08'], decimals=0))
        ))


def print_figure_1_statistics(posts_df):

    print_evolution_percentages(posts_df)

    list_complete_groups_id = []
    for id in posts_df['account_id'].unique():
        posts_df_group = posts_df[posts_df["account_id"] == id]
        if ((np.min(posts_df_group['date']) == np.min(posts_df['date'])) & 
            (np.max(posts_df_group['date']) == np.max(posts_df['date']))):
            list_complete_groups_id.append(id)
    posts_df_temp = posts_df[posts_df["account_id"].isin(list_complete_groups_id)]

    print_evolution_percentages(posts_df_temp)


def save_figure_2(posts_df):

    plot_all_groups(posts_df, title_detail="mainstream news")
    save_figure('figure_2')


def compute_main_metrics_and_their_predictors(posts_fake_df, post_url_df):

    follower_number = post_url_df[['account_id', 'account_subscriber_count']].drop_duplicates().dropna()

    link_number = post_url_df[['account_id', 'url']].drop_duplicates().dropna()
    link_number = link_number.account_id.value_counts().to_frame(name="link_number")\
        .reset_index().rename(columns={"index": "account_id"})

    vc = posts_fake_df['account_id'].value_counts()
    posts_fake_df = posts_fake_df[posts_fake_df['account_id'].isin(vc[vc > 14].index)]

    posts_fake_df['metric'] = posts_fake_df['share'] + posts_fake_df['comment'] + posts_fake_df['reaction']
    popularity = posts_fake_df.groupby(by=["account_id"])['metric'].mean().to_frame(name="mean_popularity")\
        .reset_index().rename(columns={"index": "account_id"})

    evolution_percentage = pd.Series([])
    reduced_periods_percentage = pd.Series([])
    total_days = (np.datetime64('2020-06-09') - np.datetime64('2019-09-01'))/ np.timedelta64(1, 'D')

    for account_id in posts_fake_df['account_id'].unique():

        posts_group_df = posts_fake_df[posts_fake_df['account_id']==account_id]
        serie = posts_group_df.groupby(by=["date"])['metric'].mean()
        if len(posts_group_df[posts_group_df['date']=='2020-06-08']) > 9 and len(posts_group_df[posts_group_df['date']=='2020-06-10']) > 9:
            percentage = (serie.loc['2020-06-10'] - serie.loc['2020-06-08']) * 100 / serie.loc['2020-06-08']
            evolution_percentage = evolution_percentage.append(pd.Series([percentage], index=[account_id]))
        
        reduced_periods = compute_reduced_periods(posts_fake_df, account_id)
        reduced_periods = merge_overlapping_periods(reduced_periods)
        reduced_period_length = 0
        for period in reduced_periods:
            if period[1] < np.datetime64('2020-06-09'):
                reduced_period_length += (period[1] - period[0]).days
            elif period[0] < np.datetime64('2020-06-09'):
                reduced_period_length += (np.datetime64('2020-06-09') - period[0]).days
        reduced_periods_percentage = reduced_periods_percentage.append(pd.Series([reduced_period_length*100/total_days], 
                                                                                 index=[account_id]))

    evolution_percentage = evolution_percentage.to_frame(name="percentage_evolution")\
        .reset_index().rename(columns={"index": "account_id"})
    reduced_periods_percentage = reduced_periods_percentage.to_frame(name="reduced_periods_percentage")\
        .reset_index().rename(columns={"index": "account_id"})

    evolution_percentage = evolution_percentage.merge(link_number, how='left', on='account_id')
    evolution_percentage = evolution_percentage.merge(follower_number, how='left', on='account_id')
    evolution_percentage = evolution_percentage.merge(popularity, how='left', on='account_id')

    reduced_periods_percentage = reduced_periods_percentage.merge(link_number, how='left', on='account_id')
    reduced_periods_percentage = reduced_periods_percentage.merge(follower_number, how='left', on='account_id')
    reduced_periods_percentage = reduced_periods_percentage.merge(popularity, how='left', on='account_id')

    print(len(evolution_percentage))
    return evolution_percentage, reduced_periods_percentage


def print_correlation_coefficients(df, column_to_predict):
    print("\n\nFor the " + column_to_predict + " variable:")
    for predictor in ['account_subscriber_count', 'mean_popularity', 'link_number']:
        coef = np.corrcoef(list(df[column_to_predict].values), 
                    list(df[predictor].values))[0, 1]
        print("The correlation coefficient with {} is {}.".format(predictor, np.around(coef, decimals=2)))


def plot_one_group(posts_df, account_id, plot_special_date, 
                   fake_news_dates, repeat_offender_periods):
    
    posts_df_group = posts_df[posts_df["account_id"] == account_id]
    
    plt.plot(posts_df_group.groupby(by=["date"])["reaction"].mean(), 
            label="Mean number of reactions per post")

    plt.plot(posts_df_group.groupby(by=["date"])["comment"].mean(), 
            label="Mean number of comments per post")
    
    details_temporal_evolution(posts_df, plot_special_date)

    scale_y = np.max([np.max(posts_df_group.groupby(by=["date"])["reaction"].mean()),
                     np.max(posts_df_group.groupby(by=["date"])["comment"].mean())])/10

    for date in fake_news_dates:
        plt.arrow(x=date, y=0, dx=0, dy=-scale_y, color='C3')
    
    for period in repeat_offender_periods:
        plt.axvspan(period[0], period[1], ymin=0, ymax=1/11, facecolor='C3', alpha=0.2)

    plt.hlines(0, xmin=np.datetime64('2019-08-28'), xmax=np.datetime64('2020-09-04'), linewidths=1)
    plt.ylim(bottom=-scale_y)


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

        potential_dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in potential_dates]
        date_to_plot = np.datetime64(np.max(potential_dates))
        fake_news_dates.append(date_to_plot)
        
    fake_news_dates = [date for date in fake_news_dates if date >= np.datetime64('2019-09-01')]
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


def compute_reduced_periods(posts_df, account_id):

    posts_df_group = posts_df[posts_df["account_id"] == account_id]
    posts_df_group = posts_df_group.sort_values(by=['date'])
    posts_df_group['metrics'] = posts_df_group['reaction'] + posts_df_group['comment']
    
    time_series = posts_df_group.groupby(by=["date"])["metrics"].mean()
    global_mean = np.mean(time_series[time_series.index < np.datetime64("2020-06-09")].values)
    global_std = np.std(time_series[time_series.index < np.datetime64("2020-06-09")].values)
    zscores = (time_series - global_mean)/global_std
    
    reduced_periods = []
    for index in range(len(time_series.index) - 14):
        sample_zscores = zscores[index:index + 14]
        if (np.sum(sample_zscores) < - 14) & (np.mean(time_series[index:index + 14]) < global_mean/1.5):
            if len(sample_zscores[sample_zscores<-1]) > 1:
                reduced_periods.append([sample_zscores[sample_zscores<-1].index[0], 
                                        sample_zscores[sample_zscores<-1].index[-1]])

    return reduced_periods


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


def compute_drastic_change_dates(df):
    
    df['metrics'] = df['reaction'] + df['comment']
    df['date'] = df['date'] - pd.to_timedelta(4, unit='d')
    df_temp = df[['date', 'metrics']].resample('W-Mon', on='date').mean().reset_index()

    decreasing_dates = []
    increasing_dates = []

    for index in df_temp.index[3:]:
        before_serie = df_temp[(index-3):(index-1)]['metrics'].values
        after_serie = df_temp[index:index+2]['metrics'].values

        if np.max(after_serie) < np.min(before_serie)/2:
            decreasing_dates.append(df_temp.iloc[index]['date'])
        elif np.max(before_serie) < np.min(after_serie)/2:
            increasing_dates.append(df_temp.iloc[index]['date'])
            
    return decreasing_dates, increasing_dates


# example:
# posts_df_group = posts_df[posts_df["account_id"] == account_id]
# decreasing_dates, increasing_dates = compute_drastic_change_dates(posts_df_group)
# reduced_periods = compute_periods_from_date_lists(decreasing_dates, increasing_dates, DATE)
# reduced_periods = merge_overlapping_periods(reduced_periods)


def compute_periods_from_date_lists(decreasing_dates, increasing_dates, DATE):
    
    reduced_periods = []
    for each_decreasing_date in decreasing_dates:
        
        next_increasing_date = [date for date in increasing_dates if date > each_decreasing_date]
        if len(next_increasing_date) > 0:
            next_increasing_date = np.min(next_increasing_date)
        else:
            next_increasing_date = np.datetime64(DATE)
            
        reduced_periods.append([each_decreasing_date, next_increasing_date])
        
    return reduced_periods


def save_figure_3(posts_df, post_url_df, url_df):

    accounts_to_plot = [
        'Chemtrails Global Skywatch',
        'Conspiracy Theory & Alternative News',
        'Q The Greatest Story Ever Told',
        'Women SCOUTS for TRUMP (c)',
        'The Rush Limbaugh Facebook Group',
        'THRIVE MOVEMENT',
        'Drain The Swamp',
        'The Shift - Being the Change',
        'Australian Climate Sceptics Group',
        'S5GG - STOP 5G Global'
    ]

    plt.figure(figsize=(12, 14))

    for group_index in range(len(accounts_to_plot)):
        account_id = posts_df[posts_df['account_name']==accounts_to_plot[group_index]].account_id.unique()[0]

        ax = plt.subplot(len(accounts_to_plot)/2, 2, group_index + 1)

        fake_news_dates = compute_fake_news_dates(post_url_df, url_df, account_id)

        repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
        repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)

        reduced_periods = compute_reduced_periods(posts_df, account_id)
        reduced_periods = merge_overlapping_periods(reduced_periods)
        for period in reduced_periods:
            plt.axvspan(period[0], period[1], ymin=1/11, facecolor='C2', alpha=0.2)

        plot_one_group(posts_df, account_id, plot_special_date=False, 
                       fake_news_dates=fake_news_dates, repeat_offender_periods=repeat_offender_periods)
        
        if group_index > 0: 
            ax.get_legend().set_visible(False)

        plt.title(accounts_to_plot[group_index])

    plt.tight_layout()
    save_figure('figure_3')


def plot_the_groups_one_by_one(posts_df, post_url_df, url_df):

    group_index = 0
    for account_id in posts_df['account_id'].unique():

        posts_df_group = posts_df[posts_df["account_id"] == account_id]
        time_series = posts_df_group.groupby(by=["date"])["reaction"].mean()

        if len(time_series) > 350:

            if group_index % 10 == 0:
                plt.figure(figsize=(12, 14))

            ax = plt.subplot(5, 2, group_index % 10 + 1)

            fake_news_dates = compute_fake_news_dates(post_url_df, url_df, account_id)

            repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
            repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)

            reduced_periods = compute_reduced_periods(posts_df, account_id)
            reduced_periods = merge_overlapping_periods(reduced_periods)
            for period in reduced_periods:
                plt.axvspan(period[0], period[1], ymin=1/11, facecolor='C2', alpha=0.2)

            plot_one_group(posts_df, account_id, plot_special_date=False, 
                        fake_news_dates=fake_news_dates, repeat_offender_periods=repeat_offender_periods)
            plt.title(posts_df[posts_df['account_id']==account_id].account_name.unique()[0])

            if group_index % 10 != 0: 
                ax.get_legend().set_visible(False)

            if (group_index % 10 == 9) | (group_index == posts_df['account_id'].nunique() - 1):
                plt.tight_layout()
                save_figure('supplementary_figure_1_{}'.format(int(group_index / 10) + 1))
            
            group_index += 1


if __name__ == "__main__":

    DATE = "2020-08-27"
    DATE_URL_REQUEST = "2020-08-31"

    df_before, df_after = clean_comparison_data(before_date="02_06_2020", after_date="2020-08-31")
    print_table_1(df_before, df_after)
    print_table_2(df_before, df_after)

    posts_fake_df = clean_crowdtangle_group_data("fake_news")
    save_figure_1(posts_fake_df)
    print_figure_1_statistics(posts_fake_df)

    posts_main_df = clean_crowdtangle_group_data("main_news")
    save_figure_2(posts_main_df)

    post_url_df = import_data(folder="data_crowdtangle_url", file_name="posts_url_" + DATE_URL_REQUEST + "_.csv")
    evolution_percentage, reduced_periods_percentage = compute_main_metrics_and_their_predictors(posts_fake_df, post_url_df)
    print_correlation_coefficients(evolution_percentage, 'percentage_evolution')
    print_correlation_coefficients(reduced_periods_percentage, 'reduced_periods_percentage')

    url_df = import_data(folder="data_sciencefeedback", file_name="appearances_" + DATE + "_.csv")
    post_url_df = clean_crowdtangle_url_data(post_url_df, url_df)    
    save_figure_3(posts_fake_df, post_url_df, url_df)

    # plot_the_groups_one_by_one(posts_fake_df, post_url_df, url_df)
