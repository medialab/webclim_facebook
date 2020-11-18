import os
import warnings
import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches


warnings.filterwarnings("ignore")
pd.options.display.max_colwidth = 300


def import_data(folder, file_name):
    data_path = os.path.join(".", "data", folder, file_name)
    df = pd.read_csv(data_path)
    return df


def keep_only_one_year_data(df):
    df['date'] = pd.to_datetime(df['date'])
    df = df[df['date'] < np.max(df['date'])]
    df = df[df['date'] > np.max(df['date']) - datetime.timedelta(days=366)]
    return df


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


def save_figure(figure_name):

    figure_path = os.path.join('.', 'figure', figure_name + '.png')
    plt.savefig(figure_path)

    print('\n\n' + figure_name.upper())
    print("The '{}' figure has been saved in the '{}' folder."\
        .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


def details_temporal_evolution(posts_df, ax):

    plt.axvline(x=np.datetime64("2020-06-09"), color='black', linestyle='--', linewidth=1)

    plt.legend()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))

    plt.locator_params(axis='y', nbins=4)

    plt.xlim(
        np.datetime64(datetime.datetime.strptime('2019-09-01', '%Y-%m-%d') - datetime.timedelta(days=4)), 
        np.datetime64(datetime.datetime.strptime('2020-08-31', '%Y-%m-%d') + datetime.timedelta(days=4))
    )
    plt.ylim(bottom=0)

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.grid(axis="y")


def plot_all_groups(posts_df, title_detail):

    plt.figure(figsize=(8, 10))

    ax = plt.subplot(311)
    plt.title("Evolution of Facebook interaction metrics averaged for {} '".format(posts_df["account_id"].nunique()) + title_detail + "' accounts")
    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df["date"].value_counts().sort_index(), 
            label="Reactions per post")
    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df["date"].value_counts().sort_index(), 
            label="Shares per post")
    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df["date"].value_counts().sort_index(), 
            label="Comments per post")
    details_temporal_evolution(posts_df, ax)

    ax = plt.subplot(312)

    plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
        label="Posts per day", color=[.2, .2, .2])

    details_temporal_evolution(posts_df, ax)

    ax = plt.subplot(313)

    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Reactions per day")
    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Shares per day")
    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Comments per day")
    details_temporal_evolution(posts_df, ax)

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

    link_number = post_url_df[post_url_df['date'] < np.datetime64('2020-06-09')]
    link_number = link_number[['account_id', 'url']].drop_duplicates().dropna()
    link_number = link_number.account_id.value_counts().to_frame(name="link_number")\
        .reset_index().rename(columns={"index": "account_id"})

    vc = posts_fake_df['account_id'].value_counts()
    posts_fake_df = posts_fake_df[posts_fake_df['account_id'].isin(vc[vc > 14].index)]

    posts_fake_df['metric'] = posts_fake_df['share'] + posts_fake_df['comment'] + posts_fake_df['reaction']
    popularity = posts_fake_df.groupby(by=["account_id"])['metric'].mean().to_frame(name="mean_popularity")\
        .reset_index().rename(columns={"index": "account_id"})

    evolution_percentage = pd.Series([])
    for account_id in posts_fake_df['account_id'].unique():

        posts_group_df = posts_fake_df[posts_fake_df['account_id']==account_id]
        serie = posts_group_df.groupby(by=["date"])['metric'].mean()
        if len(posts_group_df[posts_group_df['date']=='2020-06-08']) > 9 and len(posts_group_df[posts_group_df['date']=='2020-06-10']) > 9:
            percentage = (serie.loc['2020-06-10'] - serie.loc['2020-06-08']) * 100 / serie.loc['2020-06-08']
            evolution_percentage = evolution_percentage.append(pd.Series([percentage], index=[account_id]))

    evolution_percentage = evolution_percentage.to_frame(name="percentage_evolution")\
        .reset_index().rename(columns={"index": "account_id"})

    evolution_percentage = evolution_percentage.merge(link_number, how='left', on='account_id').fillna(0)
    evolution_percentage = evolution_percentage.merge(follower_number, how='left', on='account_id')
    evolution_percentage = evolution_percentage.merge(popularity, how='left', on='account_id')

    return evolution_percentage


def save_supplementary_figure_1(evolution_percentage):

    plt.figure(figsize=(12, 4))

    plt.subplot(131)
    plt.scatter(evolution_percentage['account_subscriber_count'], evolution_percentage['percentage_evolution'])

    plt.xscale('log')
    plt.gca().invert_yaxis()
    plt.yticks(ticks=[150, 100, 50, 0, -50, -100], labels=['+150%', '+100%', '+50%', '0%', '-50%', '-100%'])

    plt.xlabel('Number of followers\n(in log scale)')
    plt.ylabel("Evolution rate of each account's engagement\n between June 8 and 10, 2020")

    coef = np.corrcoef(list(evolution_percentage['percentage_evolution'].values), 
                list(evolution_percentage['account_subscriber_count'].values))[0, 1]
    plt.text(80000, 150, 'r = ' + str(np.around(coef, decimals=2)))

    plt.subplot(132)
    plt.scatter(evolution_percentage['mean_popularity'], evolution_percentage['percentage_evolution'])

    plt.gca().invert_yaxis()
    plt.yticks(ticks=[150, 100, 50, 0, -50, -100], labels=['', '', '', '', '', ''])

    plt.xscale('log')
    plt.xlabel('Mean engagement per post\n(in log scale)')

    coef = np.corrcoef(list(evolution_percentage['percentage_evolution'].values), 
                list(evolution_percentage['mean_popularity'].values))[0, 1]
    plt.text(90, 150, 'r = ' + str(np.around(coef, decimals=2)))

    plt.subplot(133)
    plt.scatter(evolution_percentage['link_number'], evolution_percentage['percentage_evolution'])

    plt.gca().invert_yaxis()
    plt.yticks(ticks=[150, 100, 50, 0, -50, -100], labels=['', '', '', '', '', ''])

    plt.xscale('log')
    plt.xticks(ticks=[20, 30, 40, 60, 100], labels=['20', '30', '40', '60', '100'])
    plt.xlabel('Number of shared misinformation links\n(in log scale)')

    coef = np.corrcoef(list(evolution_percentage['percentage_evolution'].values), 
                list(evolution_percentage['link_number'].values))[0, 1]
    plt.text(70, 150, 'r = ' + str(np.around(coef, decimals=2)))

    plt.tight_layout()
    save_figure('supplementary_figure_1')


def print_correlation_coefficients(df, column_to_predict):
    print("\n\nFor the " + column_to_predict + " variable:")
    for predictor in ['account_subscriber_count', 'mean_popularity', 'link_number']:
        coef = np.corrcoef(list(df[column_to_predict].values), 
                    list(df[predictor].values))[0, 1]
        print("The correlation coefficient with {} is {}.".format(predictor, np.around(coef, decimals=2)))


def rolling_average_per_day(df, column):
    return df.groupby(by=["date"])[column].mean()


def plot_one_group(posts_df, account_id, fake_news_dates):
    
    posts_df_group = posts_df[posts_df["account_id"] == account_id]
    
    plt.plot(rolling_average_per_day(posts_df_group, 'reaction'), 
            label="Reactions per post", color="C0")

    plt.plot(rolling_average_per_day(posts_df_group, 'comment'), 
            label="Comments per post", color="C2")

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))

    plt.locator_params(axis='y', nbins=4)

    plt.xlim(
        np.datetime64(datetime.datetime.strptime('2019-09-01', '%Y-%m-%d') - datetime.timedelta(days=4)), 
        np.datetime64(datetime.datetime.strptime('2020-08-31', '%Y-%m-%d') + datetime.timedelta(days=4))
    )

    scale_y = np.nanmax([rolling_average_per_day(posts_df_group, 'reaction'),
                        rolling_average_per_day(posts_df_group, 'comment')])/10

    for date in fake_news_dates:
        plt.arrow(x=date, y=0, dx=0, dy=-scale_y, color='C3')

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

        potential_dates = [np.datetime64(date) for date in potential_dates]
        date_to_plot = np.max(potential_dates)
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


def save_figure_3(posts_df, post_url_df, url_df):

    accounts_to_plot = [
        'Exposing The New World Order',
        'Truth Revolution',
        'Women SCOUTS for TRUMP (c)',
        'Climate Change Battle Royale',
        'Conspiracy Theory & Alternative News',
        'S5GG - STOP 5G Global',
        'Pharmaceuticals Exposed',
        'Stop GeoEngineering, Chemtrails, Bio-hacking CRISPR, WeDoNotConsent'
    ]

    plt.figure(figsize=(12, 10))

    for group_index in range(len(accounts_to_plot)):
        account_id = posts_df[posts_df['account_name']==accounts_to_plot[group_index]].account_id.unique()[0]

        ax = plt.subplot(4, 2, group_index + 1)

        fake_news_dates = compute_fake_news_dates(post_url_df, url_df, account_id)
        plot_one_group(posts_df, account_id, fake_news_dates=fake_news_dates)

        repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
        repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)
        for period in repeat_offender_periods:
            plt.axvspan(period[0], period[1], ymin=1/11, facecolor='C3', alpha=0.1)

        if group_index == 1: 
            plt.legend(framealpha=1)

        if group_index == 0:
            plt.text(
                s='Known strikes', color='C3',
                x=np.datetime64('2020-02-15'), horizontalalignment='left', 
                y=-1, verticalalignment='top'
            )
            patch1 = mpatches.Patch(facecolor='pink', alpha=0.4, edgecolor='k')
            patch2 = mpatches.Patch(facecolor='white', alpha=0.4, edgecolor='k')
            plt.legend([patch1, patch2], ["'Repeat offender' period", "'Free' period"],
                       loc='upper left', framealpha=1)

        if accounts_to_plot[group_index] == 'Truth Revolution':
            plt.ylim([-5, 50])

        plt.title(accounts_to_plot[group_index])
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.grid(axis="y")

    plt.tight_layout()
    save_figure('figure_3')


def save_supplementary_figure_2(posts_df, post_url_df, url_df):

    group_index = 0
    for account_id in posts_df['account_id'].unique():

        posts_df_group = posts_df[posts_df["account_id"] == account_id]
        time_series = posts_df_group.groupby(by=["date"])["reaction"].mean()

        if len(time_series) > 350:

            if group_index % 10 == 0:
                plt.figure(figsize=(12, 14))

            ax = plt.subplot(5, 2, group_index % 10 + 1)

            fake_news_dates = compute_fake_news_dates(post_url_df, url_df, account_id)
            plot_one_group(posts_df, account_id, fake_news_dates=fake_news_dates)
            plt.title(posts_df[posts_df['account_id']==account_id].account_name.unique()[0])

            repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
            repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)
            for period in repeat_offender_periods:
                plt.axvspan(period[0], period[1], ymin=1/11, facecolor='C3', alpha=0.1)

            if group_index % 10 != 0: 
                ax.get_legend().set_visible(False)

            if (group_index % 10 == 9) | (group_index == posts_df['account_id'].nunique() - 1):
                plt.tight_layout()
                save_figure('supplementary_figure_2_{}'.format(int(group_index / 10) + 1))
            
            group_index += 1


if __name__ == "__main__":

    # posts_url_before = import_data(folder="data_crowdtangle_url", file_name="posts_url_2020-06-02_.csv")
    # posts_url_before = keep_only_one_year_data(posts_url_before)
    # posts_url_before = clean_crowdtangle_url_data(posts_url_before)
    
    posts_url_after  = import_data(folder="data_crowdtangle_url", file_name="posts_url_2020-08-31_.csv")
    posts_url_after  = keep_only_one_year_data(posts_url_after)
    posts_url_after = clean_crowdtangle_url_data(posts_url_after)

    # print_table_1(posts_url_before, posts_url_after)
    # print_table_2(posts_url_before, posts_url_after)

    posts_fake = clean_crowdtangle_group_data("fake_news")
    save_figure_1(posts_fake)
    # print_figure_1_statistics(posts_fake)

    posts_main = clean_crowdtangle_group_data("main_news")
    save_figure_2(posts_main)

    # evolution_percentage = compute_main_metrics_and_their_predictors(posts_fake, posts_url_after)
    # save_supplementary_figure_1(evolution_percentage)
    # print_correlation_coefficients(evolution_percentage, 'percentage_evolution')

    url_df = import_data(folder="data_sciencefeedback", file_name="appearances_2020-08-27_.csv")    
    save_figure_3(posts_fake, posts_url_after, url_df)

    ## Plot all the groups with more than 250 datapoints
    # save_supplementary_figure_2(posts_fake, posts_url_after, url_df)
