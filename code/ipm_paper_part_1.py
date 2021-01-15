import os
import warnings
import datetime
import random

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import scipy.stats as stats

from utils import import_data, save_figure, clean_crowdtangle_url_data


warnings.filterwarnings("ignore")
pd.options.display.max_colwidth = 300


def concatenate_crowdtangle_group_data(suffix):

    if suffix == "fake_news_2021":
        df_list = []
        for file_index in range(5):
            df_list.append(import_data(folder="crowdtangle_group", 
                file_name="posts_" + suffix + "_group_" + str(file_index + 1) + ".csv"))
        posts_group_df = pd.concat(df_list)  
    else:
        posts_group_df = import_data(folder="crowdtangle_group", 
                                    file_name="posts_" + suffix + "_group.csv")

    print('\nThere are {} Facebook groups about {}.'.format(posts_group_df.account_id.nunique(), suffix))

    posts_page_df = import_data(folder="crowdtangle_group", 
                                file_name="posts_" + suffix + "_page.csv")
    print('There are {} Facebook pages about {}.'.format(posts_page_df.account_id.nunique(), suffix))

    posts_df = pd.concat([posts_group_df, posts_page_df])

    posts_df['date'] = pd.to_datetime(posts_df['date'])
    # posts_df = posts_df[posts_df['date'] >= datetime.datetime.strptime('2019-09-01', '%Y-%m-%d')]
    # posts_df = posts_df[posts_df['date'] <= datetime.datetime.strptime('2020-08-31', '%Y-%m-%d')]

    return posts_df


def details_temporal_evolution(posts_df, ax):

    plt.axvline(x=np.datetime64("2020-06-09"), color='black', linestyle='--', linewidth=1)

    plt.legend()

    xticks = [np.datetime64('2019-01-01'), np.datetime64('2019-03-01'), np.datetime64('2019-05-01'), 
              np.datetime64('2019-07-01'), np.datetime64('2019-09-01'), np.datetime64('2019-11-01'),
              np.datetime64('2020-01-01'), np.datetime64('2020-03-01'), np.datetime64('2020-05-01'), 
              np.datetime64('2020-07-01'), np.datetime64('2020-09-01'), np.datetime64('2020-11-01'),
             ]
    plt.xticks(xticks, rotation=30, ha='right')

    plt.locator_params(axis='y', nbins=4)

    plt.xlim(
        np.datetime64(datetime.datetime.strptime('2018-12-31', '%Y-%m-%d') - datetime.timedelta(days=4)), 
        np.datetime64(datetime.datetime.strptime('2021-01-01', '%Y-%m-%d') + datetime.timedelta(days=4))
    )
    plt.ylim(bottom=0)

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.grid(axis="y")


def plot_group_average(posts_df, title_detail):

    plt.figure(figsize=(10, 12))

    ax = plt.subplot(311)
    plt.title("'" + title_detail + "' accounts", fontsize='x-large')
    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Reactions per day")
    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Shares per day")
    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Comments per day")
    details_temporal_evolution(posts_df, ax)

    ax = plt.subplot(312)
    plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
        label="Posts per day", color=[.2, .2, .2])
    details_temporal_evolution(posts_df, ax)

    ax = plt.subplot(313)
    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df["date"].value_counts().sort_index(), 
            label="Reactions per post")
    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df["date"].value_counts().sort_index(), 
            label="Shares per post")
    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df["date"].value_counts().sort_index(), 
            label="Comments per post")
    details_temporal_evolution(posts_df, ax)

    plt.tight_layout()


def save_figure_2(posts_fake):
    plot_group_average(posts_fake, title_detail="Misinformation")
    save_figure('figure_2', folder='ip&m', dpi=100)


def save_figure_3(posts_main):
    plot_group_average(posts_main, title_detail="Established news")
    save_figure('figure_3', folder='ip&m', dpi=100)


def print_evolution_percentages(posts_df):
    print('\nFor the {} Facebook accounts about fake news:'.format(posts_df.account_id.nunique()))

    for metric in ['reaction', 'share', 'comment']:
        serie = posts_df.groupby(by=["date", 'account_id'])[metric].mean().groupby(by=['date']).mean()
        print('The ' + metric +'s has evolved by {}% between June 8 and 10, 2020.'.format(
            int(np.around((serie.loc['2020-06-10'] - serie.loc['2020-06-08']) * 100 / serie.loc['2020-06-08'], decimals=0))
        ))


def print_figure_2_statistics(posts_df):

    print_evolution_percentages(posts_df)

    all_accounts_index = 0
    declining_accounts_index = 0

    for account_id in posts_df['account_id'].unique():
        posts_df_group = posts_df[posts_df["account_id"] == account_id]
        reaction_serie = posts_df_group.groupby(by=["date"])['reaction'].mean()
        share_serie = posts_df_group.groupby(by=["date"])['share'].mean()
        comment_serie = posts_df_group.groupby(by=["date"])['comment'].mean()

        if ('2020-06-08' in reaction_serie.index) and ('2020-06-10' in reaction_serie.index):
            all_accounts_index += 1
            if ((reaction_serie.loc['2020-06-10'] < reaction_serie.loc['2020-06-08']) and 
                (share_serie.loc['2020-06-10'] < share_serie.loc['2020-06-08']) and 
                (comment_serie.loc['2020-06-10'] < comment_serie.loc['2020-06-08'])):
                declining_accounts_index += 1

    print('\nAmong the {} misinformation accounts, {} of them see their three engagement metrics decline.'\
            .format(all_accounts_index, declining_accounts_index))

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


def plot_one_group(ax, posts_df, account_id, fake_news_dates):
    
    posts_df_group = posts_df[posts_df["account_id"] == account_id]
    
    plt.plot(rolling_average_per_day(posts_df_group, 'reaction'), 
            label="Reactions per post", color="C0")

    plt.plot(rolling_average_per_day(posts_df_group, 'share'), 
            label="Shares per post", color="C1")

    plt.plot(rolling_average_per_day(posts_df_group, 'comment'), 
            label="Comments per post", color="C2")

    plt.locator_params(axis='y', nbins=4)
    xticks = [np.datetime64('2019-01-01'), np.datetime64('2019-05-01'), np.datetime64('2019-09-01'),
              np.datetime64('2020-01-01'), np.datetime64('2020-05-01'), np.datetime64('2020-09-01')
             ]
    plt.xticks(xticks, rotation=30, ha='right')

    plt.xlim(
        np.datetime64(datetime.datetime.strptime('2018-12-31', '%Y-%m-%d') - datetime.timedelta(days=4)), 
        np.datetime64(datetime.datetime.strptime('2021-01-01', '%Y-%m-%d') + datetime.timedelta(days=4))
    )

    scale_y = np.nanmax([rolling_average_per_day(posts_df_group, 'reaction'),
                        rolling_average_per_day(posts_df_group, 'comment'),
                        rolling_average_per_day(posts_df_group, 'share')])/10

    for date in fake_news_dates:
        plt.arrow(x=date, y=0, dx=0, dy=-scale_y, color='C3')

    plt.hlines(0, xmin=np.datetime64('2018-12-17'), xmax=np.datetime64('2021-01-04'), linewidths=1)
    plt.ylim(bottom=-scale_y)
        
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.grid(axis="y")


def compute_fake_news_dates(post_url_df, url_df, account_id):

    post_url_group_df = post_url_df[post_url_df["account_id"]==account_id]
    fake_news_dates = []

    for url in post_url_group_df["url"].unique().tolist():
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


def plot_repeat_offender_example(posts_df, post_url_df, url_df, ax):

    account_name = 'Australian Climate Sceptics Group'
    account_id = posts_df[posts_df['account_name']==account_name].account_id.unique()[0]
    fake_news_dates = compute_fake_news_dates(post_url_df, url_df, account_id)
    plot_one_group(ax, posts_df, account_id, fake_news_dates=fake_news_dates)

    repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
    repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)
    for period in repeat_offender_periods:
        plt.axvspan(period[0], period[1], ymin=1/11, facecolor='C3', alpha=0.1)

    xticks = [np.datetime64('2019-01-01'), np.datetime64('2019-03-01'), np.datetime64('2019-05-01'), 
              np.datetime64('2019-07-01'), np.datetime64('2019-09-01'), np.datetime64('2019-11-01'),
              np.datetime64('2020-01-01'), np.datetime64('2020-03-01'), np.datetime64('2020-05-01'), 
              np.datetime64('2020-07-01'), np.datetime64('2020-09-01'), np.datetime64('2020-11-01'),
             ]
    plt.xticks(xticks, rotation=30, ha='right')

    plt.text(
        s='Known strikes', color='C3', fontweight='bold',
        x=np.datetime64('2019-09-25'), horizontalalignment='right', 
        y=-2, verticalalignment='top'
    )

    legend1 = plt.legend(loc='upper left')

    patch1 = mpatches.Patch(facecolor='pink', alpha=0.4, edgecolor='k')
    patch2 = mpatches.Patch(facecolor='white', alpha=0.4, edgecolor='k')
    legend2 = plt.legend([patch1, patch2], ["'Repeat offender' periods", "'No strike' periods"],
                loc='upper right', framealpha=1)
    plt.gca().add_artist(legend1)

    plt.ylim(top=80)

    plt.title("Engagement metrics for one Facebook group example ('" + account_name + "')")


def calculate_confidence_interval(sample):

    averages = []
    for bootstrap_index in range(1000):
        resampled_sample = random.choices(sample, k=len(sample))
        averages.append(np.mean(resampled_sample))

    return np.percentile(averages, 5), np.percentile(averages, 95)


def plot_repeat_offender_average(repeat_offender, free, ax):

    width = .25
    labels = ['Reactions', 'Shares', 'Comments']
    x = np.arange(len(labels)) 

    # Plot the bars
    plt.bar(x - width/2, [np.mean(repeat_offender['reaction']), np.mean(repeat_offender['share']), 
                                        np.mean(repeat_offender['comment'])], 
                    width, label="'Repeat offender' periods", color='pink', edgecolor=[.2, .2, .2], zorder=3)
    plt.bar(x + width/2, [np.mean(free['reaction']), np.mean(free['share']), np.mean(free['comment'])], 
                    width, label="'No strike' periods", color='white', edgecolor=[.2, .2, .2], zorder=3)

    # Add the error bars
    idx = 0   
    for metric in ['reaction', 'share', 'comment']:
        low, high = calculate_confidence_interval(repeat_offender[metric])
        plt.errorbar(idx - width/2, np.mean(repeat_offender[metric]), 
            yerr=[[np.mean(repeat_offender[metric]) - low], [high - np.mean(repeat_offender[metric])]], 
            color=[.2, .2, .2], zorder=4, linestyle='')

        low, high = calculate_confidence_interval(free[metric])
        plt.errorbar(idx + width/2, np.mean(free[metric]), 
            yerr=[[np.mean(free[metric]) - low], [high - np.mean(free[metric])]], 
            color=[.2, .2, .2], zorder=4, linestyle='')

        idx += 1

    plt.legend(framealpha=1)

    plt.title("Engagement metrics averaged over {} 'misinformation' accounts"\
        .format(len(repeat_offender['reaction'])))
    plt.xticks(x, labels, fontsize='large',)
    ax.tick_params(axis='x', which='both', length=0)
    plt.xlim([-.5, 2.5])
    ax.grid(axis="y", zorder=0)
    plt.locator_params(axis='y', nbins=4)

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)


def print_repeat_offender_statistics(repeat_offender, free):
    t, p = stats.wilcoxon(repeat_offender['reaction'], free['reaction'])
    print('\nWilcoxon test between the reactions: t =', t, ', p =', p)
    t, p = stats.wilcoxon(repeat_offender['share'], free['share'])
    print('\nWilcoxon test between the shares: t =', t, ', p =', p)
    t, p = stats.wilcoxon(repeat_offender['comment'], free['comment'])
    print('\nWilcoxon test between the comments: t =', t, ', p =', p)


def save_figure_1(posts_df, post_url_df, url_df):

    fig = plt.figure(figsize=(10, 8))
    gs = fig.add_gridspec(2, 5)

    # top panel
    ax = fig.add_subplot(gs[0, :])
    plot_repeat_offender_example(posts_df, post_url_df, url_df, ax)

    # bottom panel
    repeat_offender, free = compute_periods_average(posts_df, post_url_df, url_df)
    ax = fig.add_subplot(gs[1, 1:4])
    plot_repeat_offender_average(repeat_offender, free, ax)

    plt.tight_layout(pad=3)
    save_figure('figure_1', folder='ip&m', dpi=100)

    print_repeat_offender_statistics(repeat_offender, free)


def save_supplementary_figure_1(posts_df, post_url_df, url_df):
    
    fig = plt.figure(figsize=(10, 12))

    accounts_to_plot = [
        'Pharmaceuticals Exposed',
        'Humanity vs Insanity - The CRANE Report',
        'News2morrow',
        'Truth Train',
        'The British Constitution Group',
        "Arnica - Parents' Support Network, Promoting Natural Immunity",
        'ROKOTUSKRIITTISET',
        'Canadian Freedom Fighters',
        "'FACEBOOK CENSORED NEWS'",
        'Tampa Bay Trump Club'
    ]

    for idx in range(len(accounts_to_plot)):
        ax = plt.subplot(5, 2, idx + 1)
        plt.title(accounts_to_plot[idx])

        account_id = posts_df[posts_df['account_name']==accounts_to_plot[idx]].account_id.unique()[0]
        fake_news_dates = compute_fake_news_dates(post_url_df, url_df, account_id)
        plot_one_group(ax, posts_df, account_id, fake_news_dates=fake_news_dates)

        repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
        repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)
        for period in repeat_offender_periods:
            plt.axvspan(period[0], period[1], ymin=1/11, facecolor='C3', alpha=0.1)

        if idx == 0:
            legend1 = plt.legend(loc='upper left')
        elif idx == 1:
            patch1 = mpatches.Patch(facecolor='pink', alpha=0.4, edgecolor='k')
            patch2 = mpatches.Patch(facecolor='white', alpha=0.4, edgecolor='k')
            legend2 = plt.legend([patch1, patch2], ["'Repeat offender' periods", "'No strike' periods"],
                        loc='upper right', framealpha=1)
        plt.axvline(x=np.datetime64("2020-06-09"), color='black', linestyle='--', linewidth=1)

    plt.tight_layout()
    save_figure('supplementary_figure_1', folder='ip&m', dpi=100)


def save_all_groups_figures(posts_df, post_url_df, url_df):

    group_index = 0
    for account_id in posts_df['account_id'].unique():

        if group_index % 10 == 0:
            plt.figure(figsize=(12, 14))

        ax = plt.subplot(5, 2, group_index % 10 + 1)

        fake_news_dates = compute_fake_news_dates(post_url_df, url_df, account_id)
        plot_one_group(ax, posts_df, account_id, fake_news_dates=fake_news_dates)
        plt.title(posts_df[posts_df['account_id']==account_id].account_name.unique()[0])

        repeat_offender_periods = compute_repeat_offender_periods(fake_news_dates)
        repeat_offender_periods = merge_overlapping_periods(repeat_offender_periods)
        for period in repeat_offender_periods:
            plt.axvspan(period[0], period[1], ymin=1/11, facecolor='C3', alpha=0.1)

        if (group_index % 10 == 9) | (group_index == posts_df['account_id'].nunique() - 1):
            plt.tight_layout()
            save_figure('z_part_1_all_groups_{}'.format(int(group_index / 10) + 1), folder='ip&m', dpi=100)

        group_index += 1


if __name__ == "__main__":

    posts_fake = concatenate_crowdtangle_group_data("fake_news_2021")

    appearance_df  = import_data(folder="crowdtangle_url", file_name="posts_url_2021-01-04_.csv")
    appearance_df = clean_crowdtangle_url_data(appearance_df)
    url_df = import_data(folder="sciencefeedback", file_name="appearances_2021-01-04_.csv")    
    save_figure_1(posts_fake, appearance_df, url_df)

    save_figure_2(posts_fake)
    # print_figure_2_statistics(posts_fake)

    posts_main = concatenate_crowdtangle_group_data("main_news_2021")
    save_figure_3(posts_main)

    save_supplementary_figure_1(posts_fake, appearance_df, url_df)
    # save_all_groups_figures(posts_fake, appearance_df, url_df)
