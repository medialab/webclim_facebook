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
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))

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


def save_figure_2(posts_fake, posts_main):

    plt.figure(figsize=(10, 7))

    for index in range(2):
        if index == 0:
            posts_df = posts_fake
            title_detail = 'Misinformation'
        else:
            posts_df = posts_main
            title_detail = 'Mainstream news'

        ax = plt.subplot(3, 2, 1 + index)
        plt.title("'" + title_detail + "' accounts", fontsize='x-large')
        plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df["date"].value_counts().sort_index(), 
                label="Reactions per post")
        plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df["date"].value_counts().sort_index(), 
                label="Shares per post")
        plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df["date"].value_counts().sort_index(), 
                label="Comments per post")
        details_temporal_evolution(posts_df, ax)

        ax = plt.subplot(3, 2, 3 + index)
        plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Posts per day", color=[.2, .2, .2])
        details_temporal_evolution(posts_df, ax)

        ax = plt.subplot(3, 2, 5 + index)
        plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
                label="Reactions per day")
        plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
                label="Shares per day")
        plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
                label="Comments per day")
        details_temporal_evolution(posts_df, ax)

    plt.tight_layout()
    save_figure('figure_2', folder='ip&m')


def print_evolution_percentages(posts_df):
    print('\nFor the {} Facebook accounts about fake news:'.format(posts_df.account_id.nunique()))

    for metric in ['reaction', 'share', 'comment']:
        serie = posts_df.groupby(by=["date", 'account_id'])[metric].mean().groupby(by=['date']).mean()
        print('The ' + metric +'s has evolved by {}% between June 8 and 10, 2020.'.format(
            int(np.around((serie.loc['2020-06-10'] - serie.loc['2020-06-08']) * 100 / serie.loc['2020-06-08'], decimals=0))
        ))


def print_figure_2_statistics(posts_df):

    print_evolution_percentages(posts_df)

    list_complete_groups_id = []
    for id in posts_df['account_id'].unique():
        posts_df_group = posts_df[posts_df["account_id"] == id]
        if ((np.min(posts_df_group['date']) == np.min(posts_df['date'])) & 
            (np.max(posts_df_group['date']) == np.max(posts_df['date']))):
            list_complete_groups_id.append(id)
    posts_df_temp = posts_df[posts_df["account_id"].isin(list_complete_groups_id)]

    print_evolution_percentages(posts_df_temp)


def rolling_average_per_day(df, column):
    return df.groupby(by=["date"])[column].mean().rolling(window=5, win_type='triang', center=True).mean()


def plot_one_group(posts_df, account_id, fake_news_dates):
    
    posts_df_group = posts_df[posts_df["account_id"] == account_id]
    
    plt.plot(rolling_average_per_day(posts_df_group, 'reaction'), 
            label="Reactions per post", color="C0")

    plt.plot(rolling_average_per_day(posts_df_group, 'share'), 
            label="Shares per post", color="C1")

    plt.plot(rolling_average_per_day(posts_df_group, 'comment'), 
            label="Comments per post", color="C2")

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))

    plt.locator_params(axis='y', nbins=4)

    plt.xlim(
        np.datetime64(datetime.datetime.strptime('2019-09-01', '%Y-%m-%d') - datetime.timedelta(days=4)), 
        np.datetime64(datetime.datetime.strptime('2020-08-31', '%Y-%m-%d') + datetime.timedelta(days=4))
    )
    plt.ylim(bottom=0)

    scale_y = np.nanmax([rolling_average_per_day(posts_df_group, 'reaction'),
                        rolling_average_per_day(posts_df_group, 'comment'),
                        rolling_average_per_day(posts_df_group, 'share')])/10

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


def compute_periods_average(posts_df, post_url_df, url_df):

    repeat_offender = {
        'reaction': [],
        'share': [],
        'comment': []
    }
    free = {
        'reaction': [],
        'share': [],
        'comment': []
    }

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

        if (len(repeat_offender_df) > 0) & (len(free_df) > 0):
            
            repeat_offender['reaction'].append(np.mean(repeat_offender_df['reaction']))
            free['reaction'].append(np.mean(free_df['reaction']))
            
            repeat_offender['share'].append(np.mean(repeat_offender_df['share']))
            free['share'].append(np.mean(free_df['share']))
            
            repeat_offender['comment'].append(np.mean(repeat_offender_df['comment']))
            free['comment'].append(np.mean(free_df['comment']))

    return repeat_offender, free


def save_figure_1(posts_df, post_url_df, url_df):

    fig = plt.figure(figsize=(10, 6))
    gs = fig.add_gridspec(2, 5)

    ## First part
    ax = fig.add_subplot(gs[0, :])

    account_name = 'Stop GeoEngineering, Chemtrails, Bio-hacking CRISPR, WeDoNotConsent'
    account_id = posts_df[posts_df['account_name']==account_name].account_id.unique()[0]
    fake_news_dates = compute_fake_news_dates(post_url_df, url_df, account_id)
    plot_one_group(posts_df, account_id, fake_news_dates=fake_news_dates)

    repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
    repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)
    for period in repeat_offender_periods:
        plt.axvspan(period[0], period[1], ymin=1/11, facecolor='C3', alpha=0.1)

    plt.text(
        s='Known strikes', color='C3',
        x=np.datetime64('2019-09-05'), horizontalalignment='left', 
        y=-1, verticalalignment='top'
    )

    legend1 = plt.legend(loc='upper left')

    patch1 = mpatches.Patch(facecolor='pink', alpha=0.4, edgecolor='k')
    patch2 = mpatches.Patch(facecolor='white', alpha=0.4, edgecolor='k')
    legend2 = plt.legend([patch1, patch2], ["'Repeat offender' periods", "'Free' periods"],
                loc='upper right', framealpha=1)
    plt.gca().add_artist(legend1)

    plt.title(account_name)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.grid(axis="y")

    ## Second part
    repeat_offender, free = compute_periods_average(posts_df, post_url_df, url_df)
    ax = fig.add_subplot(gs[1, 1:4])

    width = .25
    labels = ['Reactions', 'Shares', 'Comments']
    x = np.arange(len(labels))
    plt.bar(x - width/2, [np.mean(repeat_offender['reaction']), np.mean(repeat_offender['share']), 
                                        np.mean(repeat_offender['comment'])], 
                    width, label="'Repeat offender' periods", color='pink', edgecolor=[.2, .2, .2], zorder=3)
    plt.bar(x + width/2, [np.mean(free['reaction']), np.mean(free['share']), np.mean(free['comment'])], 
                    width, label="'Free' periods", color='white', edgecolor=[.2, .2, .2], zorder=3)
    plt.legend(framealpha=1)

    plt.title("Average over the 'misinformation' accounts")
    plt.xticks(x, labels, fontsize='large',)
    ax.tick_params(axis='x', which='both', length=0)
    plt.xlim([-.5, 2.5])
    ax.grid(axis="y", zorder=0, linestyle='--')

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.tight_layout(pad=3)
    save_figure('figure_1', folder='ip&m')

    t, p = stats.wilcoxon(repeat_offender['reaction'], free['reaction'])
    print('\nWilcoxon test between the reactions: t =', t, ', p =', p)
    t, p = stats.wilcoxon(repeat_offender['share'], free['share'])
    print('\nWilcoxon test between the shares: t =', t, ', p =', p)
    t, p = stats.wilcoxon(repeat_offender['comment'], free['comment'])
    print('\nWilcoxon test between the comments: t =', t, ', p =', p)


def save_supplementary_figure_1(posts_df, post_url_df, url_df):

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
            save_figure('supplementary_figure_1_{}'.format(int(group_index / 10) + 1), folder='ip&m')
        
        group_index += 1


if __name__ == "__main__":

    posts_fake = clean_crowdtangle_group_data("fake_news")
    posts_main = clean_crowdtangle_group_data("main_news")
    save_figure_2(posts_fake, posts_main)
    print_figure_2_statistics(posts_fake)

    appearance_df  = import_data(folder="data_crowdtangle_url", file_name="posts_url_2020-08-31_.csv")
    appearance_df  = keep_only_one_year_data(appearance_df)
    appearance_df = clean_crowdtangle_url_data(appearance_df)

    url_df = import_data(folder="data_sciencefeedback", file_name="appearances_2020-08-27_.csv")    
    save_figure_1(posts_fake, appearance_df, url_df)

    # Plot all the groups
    save_supplementary_figure_1(posts_fake, appearance_df, url_df)
