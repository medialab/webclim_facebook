import os
import warnings
import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import scipy.stats as stats

from utils import (import_data, save_figure, keep_only_one_year_data, 
                   clean_crowdtangle_url_data, clean_crowdtangle_group_data)


warnings.filterwarnings("ignore")
pd.options.display.max_colwidth = 300


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

    plt.figure(figsize=(6.5, 7))

    ax = plt.subplot(311)
    plt.title("Evolution of Facebook interaction metrics\naveraged for {} '"\
        .format(posts_df["account_id"].nunique()) + title_detail + "' accounts", fontsize='large')
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
    save_figure('figure_1', folder='ip&m')


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
    save_figure('figure_2', folder='ip&m')


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
    save_figure('supplementary_figure_1', folder='ip&m')


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
        'Stop Mandatory Vaccination',
        'Truth Revolution',
        'Women SCOUTS for TRUMP (c)',
        'Climate Change Battle Royale',
        'Conspiracy Theory & Alternative News',
        'S5GG - STOP 5G Global',
        'The British Constitution Group'
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
                y=-0.5, verticalalignment='top'
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
    save_figure('figure_3', folder='ip&m')


def keep_repeat_offender_posts(posts_df, account_id, repeat_offender_periods):

    posts_df_group = posts_df[posts_df['account_id']==account_id]
    
    if len(repeat_offender_periods) == 0:
        return pd.DataFrame()

    repeat_offender_df_list = []
    for repeat_offender_period in repeat_offender_periods:
        new_df = posts_df_group[(posts_df_group['date'] >= repeat_offender_period[0]) &
                                (posts_df_group['date'] <= repeat_offender_period[1])]
        if len(new_df) > 0:
            repeat_offender_df_list.append(new_df)
    
    if len(repeat_offender_df_list) > 0:
        return pd.concat(repeat_offender_df_list)
    else:
        return pd.DataFrame()


def keep_free_posts(posts_df, account_id, repeat_offender_periods):
    
    posts_df_group = posts_df[posts_df['account_id']==account_id]
    
    if len(repeat_offender_periods) == 0:
        return posts_df_group

    free_df_list = []
    for ro_index in range(len(repeat_offender_periods) + 1):
        if ro_index == 0:
            new_df = posts_df_group[posts_df_group['date'] < repeat_offender_periods[0][0]]
        elif ro_index == len(repeat_offender_periods):
            new_df = posts_df_group[posts_df_group['date'] > repeat_offender_periods[-1][1]]
        else:
            new_df = posts_df_group[(posts_df_group['date'] > repeat_offender_periods[ro_index - 1][1]) &
                                    (posts_df_group['date'] < repeat_offender_periods[ro_index][0])]
        if len(new_df) > 0:
            free_df_list.append(new_df)
    
    if len(free_df_list) > 0:
        return pd.concat(free_df_list)
    else:
        return pd.DataFrame()


def save_figure_4(posts_df, post_url_df, url_df):

    repeat_offender_reaction = []
    free_reaction = []

    repeat_offender_share = []
    free_share = []

    repeat_offender_comment = []
    free_comment = []

    for account_id in posts_df['account_id'].unique():
            
        fake_news_dates = compute_fake_news_dates(post_url_df, url_df, account_id)
        repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
        repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)
        
        repeat_offender_df = keep_repeat_offender_posts(posts_df, account_id, repeat_offender_periods)
        if len(repeat_offender_df) > 0:
            repeat_offender_df = repeat_offender_df[repeat_offender_df['date'] < datetime.datetime.strptime('2020-06-09', '%Y-%m-%d')]

        free_df = keep_free_posts(posts_df, account_id, repeat_offender_periods)
        if len(free_df) > 0:
            free_df = free_df[free_df['date'] < datetime.datetime.strptime('2020-06-09', '%Y-%m-%d')]

        if (len(repeat_offender_df) >= 100) & (len(free_df) >= 100):
            
            repeat_offender_reaction.append(np.mean(repeat_offender_df['reaction']))
            free_reaction.append(np.mean(free_df['reaction']))
            
            repeat_offender_share.append(np.mean(repeat_offender_df['share']))
            free_share.append(np.mean(free_df['share']))
            
            repeat_offender_comment.append(np.mean(repeat_offender_df['comment']))
            free_comment.append(np.mean(free_df['comment']))

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.grid(axis="y", zorder=0, linestyle='--')

    width = .25
    labels = ['Reactions', 'Shares', 'Comments']
    x = np.arange(len(labels))
    plt.bar(x - width/2, [np.mean(repeat_offender_reaction), np.mean(repeat_offender_share), 
                                        np.mean(repeat_offender_comment)], 
                    width, label="'Repeat offender' periods", color='pink', edgecolor=[.2, .2, .2], zorder=3)
    plt.bar(x + width/2, [np.mean(free_reaction), np.mean(free_share), np.mean(free_comment)], 
                    width, label="'Free' periods", color='white', edgecolor=[.2, .2, .2], zorder=3)
    plt.legend(framealpha=1)

    plt.xticks(x, labels)
    ax.tick_params(axis='x', which='both',length=0)
    plt.xlim([-.5, 2.5])

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)

    fig.tight_layout()
    save_figure('figure_4', folder='ip&m')

    t, p = stats.wilcoxon(repeat_offender_reaction, free_reaction)
    print('\nWilcoxon test between the reactions: t =', t, ', p =', p)
    t, p = stats.wilcoxon(repeat_offender_share, free_share)
    print('\nWilcoxon test between the shares: t =', t, ', p =', p)
    t, p = stats.wilcoxon(repeat_offender_comment, free_comment)
    print('\nWilcoxon test between the comments: t =', t, ', p =', p)


def save_supplementary_figure_2(posts_df, post_url_df, url_df):

    group_index = 0
    for account_id in posts_df['account_id'].unique():

        # posts_df_group = posts_df[posts_df["account_id"] == account_id]
        # time_series = posts_df_group.groupby(by=["date"])["reaction"].mean()

        # if len(time_series) > 350:

        if group_index % 10 == 0:
            plt.figure(figsize=(12, 14))

        plt.subplot(5, 2, group_index % 10 + 1)

        fake_news_dates = compute_fake_news_dates(post_url_df, url_df, account_id)
        plot_one_group(posts_df, account_id, fake_news_dates=fake_news_dates)
        plt.title(posts_df[posts_df['account_id']==account_id].account_name.unique()[0])

        repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
        repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)
        for period in repeat_offender_periods:
            plt.axvspan(period[0], period[1], ymin=1/11, facecolor='C3', alpha=0.1)

        if (group_index % 10 == 9) | (group_index == posts_df['account_id'].nunique() - 1):
            plt.tight_layout()
            save_figure('supplementary_figure_2_{}'.format(int(group_index / 10) + 1), folder='ip&m')
        
        group_index += 1


if __name__ == "__main__":
    
    appearance_df  = import_data(folder="data_crowdtangle_url", file_name="posts_url_2020-08-31_.csv")
    appearance_df  = keep_only_one_year_data(appearance_df)
    appearance_df = clean_crowdtangle_url_data(appearance_df)

    posts_fake = clean_crowdtangle_group_data("fake_news")
    save_figure_1(posts_fake)
    print_figure_1_statistics(posts_fake)

    posts_main = clean_crowdtangle_group_data("main_news")
    save_figure_2(posts_main)

    evolution_percentage = compute_main_metrics_and_their_predictors(posts_fake, appearance_df)
    # save_supplementary_figure_1(evolution_percentage)
    print_correlation_coefficients(evolution_percentage, 'percentage_evolution')

    url_df = import_data(folder="data_sciencefeedback", file_name="appearances_2020-08-27_.csv")    
    save_figure_3(posts_fake, appearance_df, url_df)
    save_figure_4(posts_fake, appearance_df, url_df)

    # Plot all the groups
    # save_supplementary_figure_2(posts_fake, appearance_df, url_df)
