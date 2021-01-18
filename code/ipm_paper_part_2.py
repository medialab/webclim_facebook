import os
import warnings
import re
import datetime
import json
import random
from collections import Counter

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import scipy.stats as stats

from utils import import_data, save_figure
from ipm_paper_part_1 import details_temporal_evolution, plot_one_group, calculate_confidence_interval

warnings.filterwarnings("ignore")


def import_crowdtangle_group_data():

    posts_wi_date_df = import_data(folder="crowdtangle_group", 
                                   file_name="posts_self_declared_wi_date.csv")
    print('\nThere are {} Facebook pages with the last strike date visible on the screenshot.'.\
        format(posts_wi_date_df.account_id.nunique()))

    posts_wo_date_df = import_data(folder="crowdtangle_group", 
                                   file_name="posts_self_declared_wo_date.csv")
    list_wo_name = [
        'Artists For A Free World',
        'Terrence K Williams',
        'Ben Garrison Cartoons',
        'Wendy Bell Radio',
        'New Independence Network',
        'Pruden POD & Post',
        'PR Conservative',
        'Org of Conservative Trump Americans',
        'Con Ciencia Indigena',
        'Republican Party of Lafayette County',
        'The Daily Perspective Podcast',
        'Freedom Memes',
        'White Dragon Society',
        'Robertson Family Values'
    ]
    posts_wo_date_df = posts_wo_date_df[~posts_wo_date_df['account_name'].isin(list_wo_name)]
    print('There are {} Facebook pages without the last strike date visible on the screenshot.'.\
        format(posts_wo_date_df.account_id.nunique()))

    posts_df = pd.concat([posts_wi_date_df, posts_wo_date_df])

    posts_df['date'] = pd.to_datetime(posts_df['date'])

    return posts_df


def save_figure_4(posts_df, pages_df):

    account_name = 'I Love Carbon Dioxide'
    account_id = posts_df[posts_df['account_name']==account_name].account_id.unique()[0]
    reduced_distribution_date = pages_df[pages_df['page_name'] == account_name]['date'].values[0]

    plt.figure(figsize=(10, 4))
    ax = plt.subplot()
    
    plt.title(account_name, size="x-large")

    plot_one_group(ax, posts_df, account_id, fake_news_dates=[])

    xticks = [np.datetime64('2019-01-01'), np.datetime64('2019-03-01'), np.datetime64('2019-05-01'), 
              np.datetime64('2019-07-01'), np.datetime64('2019-09-01'), np.datetime64('2019-11-01'),
              np.datetime64('2020-01-01'), np.datetime64('2020-03-01'), 
              np.datetime64('2020-07-01'), np.datetime64('2020-09-01'), np.datetime64('2020-11-01'), 
              np.datetime64(reduced_distribution_date)
             ]
    plt.xticks(xticks, rotation=30, ha='right')
    plt.gca().get_xticklabels()[-1].set_color('red')

    plt.axvline(x=np.datetime64(reduced_distribution_date), 
                color='C3', linestyle='--', linewidth=2)

    plt.legend()
    plt.tight_layout()
    save_figure('figure_4', folder='ip&m', dpi=100)


def compute_periods_average(posts_df, pages_df, period_length=7):

    before_date = {
        'reaction': [],
        'share': [],
        'comment': [],
        'post_nb': []
    }
    after_date = {
        'reaction': [],
        'share': [],
        'comment': [],
        'post_nb': []
    }

    for account_id in posts_df['account_id'].unique():

        account_name = posts_df[posts_df['account_id']==account_id].account_name.unique()[0]
        reduced_distribution_date = pages_df[pages_df['page_name'] == account_name]['date'].values[0]
        reduced_distribution_date = datetime.datetime.strptime(str(reduced_distribution_date)[:10], '%Y-%m-%d')
        posts_df_group = posts_df[posts_df["account_id"] == account_id]

        posts_df_group_before = posts_df_group[
            (posts_df_group['date'] > reduced_distribution_date - datetime.timedelta(days=period_length)) &
            (posts_df_group['date'] < reduced_distribution_date)
        ]
        posts_df_group_after = posts_df_group[
            (posts_df_group['date'] > reduced_distribution_date) &
            (posts_df_group['date'] < reduced_distribution_date + datetime.timedelta(days=period_length))
        ]
            
        if (len(posts_df_group_before) > 0) & (len(posts_df_group_after) > 0):
            
            before_date['reaction'].append(np.mean(posts_df_group_before['reaction']))
            after_date['reaction'].append(np.mean(posts_df_group_after['reaction']))

            before_date['share'].append(np.mean(posts_df_group_before['share']))
            after_date['share'].append(np.mean(posts_df_group_after['share']))

            before_date['comment'].append(np.mean(posts_df_group_before['comment']))
            after_date['comment'].append(np.mean(posts_df_group_after['comment']))

            before_date['post_nb'].append(len(posts_df_group_before))
            after_date['post_nb'].append(len(posts_df_group_after))

    return before_date, after_date


def print_before_after_statistics(before_date, after_date):

    t, p = stats.wilcoxon(before_date['reaction'], after_date['reaction'])
    print('\nWilcoxon test between the reactions: t =', t, ', p =', p)

    t, p = stats.wilcoxon(before_date['share'], after_date['share'])
    print('\nWilcoxon test between the shares: t =', t, ', p =', p)

    t, p = stats.wilcoxon(before_date['comment'], after_date['comment'])
    print('\nWilcoxon test between the comments: t =', t, ', p =', p)

    t, p = stats.wilcoxon(before_date['post_nb'], after_date['post_nb'])
    print('\nWilcoxon test between the number of posts: t =', t, ', p =', p)
    print(np.mean(before_date['post_nb']), np.mean(after_date['post_nb']))


def plot_before_after_bars(before_date, after_date, ax):

    width = .25
    labels = ['Reactions', 'Shares', 'Comments', 'Number of posts']
    x = np.arange(len(labels)) 

    # Plot the bars
    plt.bar(x - width/2, [np.mean(before_date['reaction']), np.mean(before_date['share']), 
                            np.mean(before_date['comment']), np.mean(before_date['post_nb'])], 
                    width, label="7 days before the reduced distribution date", color='paleturquoise', edgecolor=[.2, .2, .2], zorder=3)
    plt.bar(x + width/2, [np.mean(after_date['reaction']), np.mean(after_date['share']), 
                            np.mean(after_date['comment']), np.mean(after_date['post_nb'])], 
                    width, label="7 days after the reduced distribution date", color='navajowhite', edgecolor=[.2, .2, .2], zorder=3)

    # Add the error bars
    idx = 0   
    for metric in ['reaction', 'share', 'comment', 'post_nb']:
        low, high = calculate_confidence_interval(before_date[metric])
        plt.errorbar(idx - width/2, np.mean(before_date[metric]), 
            yerr=[[np.mean(before_date[metric]) - low], [high - np.mean(before_date[metric])]], 
            color=[.2, .2, .2], zorder=4, linestyle='')

        low, high = calculate_confidence_interval(after_date[metric])
        plt.errorbar(idx + width/2, np.mean(after_date[metric]), 
            yerr=[[np.mean(after_date[metric]) - low], [high - np.mean(after_date[metric])]], 
            color=[.2, .2, .2], zorder=4, linestyle='')

        idx += 1

    plt.legend(framealpha=1)

    plt.title("Engagement metrics averaged over {} 'reduced distribution' accounts"\
        .format(len(before_date['reaction'])))
    plt.xticks(x, labels, fontsize='large',)
    ax.tick_params(axis='x', which='both', length=0)
    plt.xlim([-.5, 3.5])
    ax.grid(axis="y", zorder=0)
    plt.locator_params(axis='y', nbins=8)

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)


def save_figure_5(posts_df, pages_df, period_length=7):

    before_date, after_date = compute_periods_average(posts_df, pages_df, period_length=period_length)
    print_before_after_statistics(before_date, after_date)

    _, ax = plt.subplots(figsize=(10, 4))
    plot_before_after_bars(before_date, after_date, ax)
    plt.tight_layout()
    save_figure('figure_5', folder='ip&m', dpi=100)


def save_all_groups_figures(posts_df, pages_df):

    group_index = 0
    for account_id in posts_df['account_id'].unique():

        if group_index % 10 == 0:
            plt.figure(figsize=(12, 14))

        ax = plt.subplot(5, 2, group_index % 10 + 1)
        
        account_name = posts_df[posts_df['account_id']==account_id].account_name.unique()[0]
        plt.title(account_name, size="x-large")
        reduced_distribution_date = pages_df[pages_df['page_name'] == account_name]['date'].values[0]

        plot_one_group(ax, posts_df, account_id, fake_news_dates=[])

        xticks = [np.datetime64('2019-01-01'), np.datetime64('2019-05-01'), np.datetime64('2019-09-01'),
                  np.datetime64('2020-01-01'), np.datetime64('2020-05-01'), np.datetime64('2020-09-01'),
                  np.datetime64(reduced_distribution_date)]
        plt.xticks(xticks, rotation=30, ha='right')
        plt.gca().get_xticklabels()[-1].set_color('red')
        plt.axvline(x=np.datetime64(reduced_distribution_date), 
                    color='C3', linestyle='--', linewidth=2)

        if group_index % 10 == 0: 
            plt.legend()

        if (group_index % 10 == 9) | (group_index == posts_df['account_id'].nunique() - 1):
            plt.tight_layout()
            save_figure('z_part_2_all_groups_{}'.format(int(group_index / 10) + 1), folder='ip&m', dpi=100)

        group_index += 1


if __name__ == "__main__":
    
    posts_df = import_crowdtangle_group_data()
    pages_df = import_data(folder="crowdtangle_list", file_name="self_declared_page_details.csv")
    pages_df['date'] = pd.to_datetime(pages_df['date'])

    # save_figure_4(posts_df, pages_df)
    # save_figure_5(posts_df, pages_df)

    # screenshot_df = import_data(folder="crowdtangle_post_by_id", file_name='screenshot_posts.csv')
    # print('\n\nOVERPERFORMING SCORE ANALYSIS')
    # print('The average score is {}.'.format(np.nanmean(screenshot_df['score'].values)))
    # print('Only {} posts have a positive score.'.format(len(screenshot_df[screenshot_df['score'] > 0])))

    save_all_groups_figures(posts_df, pages_df)
