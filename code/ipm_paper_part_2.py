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
from ipm_paper_part_1 import details_temporal_evolution, plot_one_group

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


def import_json(folder, file_name):
    data_path = os.path.join('.', 'data', folder, file_name)
    with open(data_path) as json_file:
        data = json.load(json_file)
    return data


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


def add_layout_details(ax):

    plt.axvline(x=0, color='C3', linestyle='--', linewidth=2)

    plt.legend()
    plt.xticks(ticks=[-7, 0, 7], labels=['7 days before', 'Alleged date', '7 days after'])
    plt.ylim(bottom=0)
    plt.locator_params(axis='y', nbins=3)
    ax.grid(axis="y")

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)


def save_figure_5(posts_df, repeat_offender_date):

    reaction_before = []
    share_before = []
    comment_before = []
    posts_before = []

    reaction_after = []
    share_after = []
    comment_after = []
    posts_after = []

    df_reaction = pd.DataFrame(index=list(range(-7, 8)))
    df_share = pd.DataFrame(index=list(range(-7, 8)))
    df_comment = pd.DataFrame(index=list(range(-7, 8)))

    df_post_number = pd.DataFrame(index=list(range(-7, 8)))

    for account_name in posts_df['account_name'].unique():

        posts_df_group = posts_df[posts_df["account_name"] == account_name] 
        posts_df_group = posts_df_group[
            (posts_df_group['date'] >= datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d') - datetime.timedelta(days=7)) &
            (posts_df_group['date'] <= datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d') + datetime.timedelta(days=7))
        ]

        if len(posts_df_group.groupby(by=["date"])["reaction"].mean().values) == 15:

            reaction_before.append(np.mean(posts_df_group[posts_df_group['date'] < datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d')]['reaction']))
            reaction_after.append(np.mean(posts_df_group[posts_df_group['date'] > datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d')]['reaction']))

            share_before.append(np.mean(posts_df_group[posts_df_group['date'] < datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d')]['share']))
            share_after.append(np.mean(posts_df_group[posts_df_group['date'] > datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d')]['share']))

            comment_before.append(np.mean(posts_df_group[posts_df_group['date'] < datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d')]['comment']))
            comment_after.append(np.mean(posts_df_group[posts_df_group['date'] > datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d')]['comment']))

            df_reaction[account_name] = posts_df_group.groupby(by=["date"])["reaction"].mean().values
            df_share[account_name] = posts_df_group.groupby(by=["date"])["share"].mean().values
            df_comment[account_name] = posts_df_group.groupby(by=["date"])["comment"].mean().values

        post_number = posts_df_group["date"].value_counts().to_frame()
        post_number = post_number.rename(columns={"date": "post_number"})
        post_number['date'] = post_number.index
        post_number['relative_date'] = post_number['date'] - datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d')
        post_number['relative_date'] = post_number['relative_date'].apply(lambda x: x.days)
        post_number = post_number.drop(columns=['date'])

        default_post_number = pd.DataFrame({'relative_date': list(range(-7, 8))})
        post_number = post_number.merge(default_post_number, on='relative_date', how='outer')\
            .sort_values(by=['relative_date']).reset_index(drop=True)
        post_number['post_number'] = post_number['post_number'].fillna(0).astype(int)

        df_post_number[account_name] = post_number['post_number'].values
        posts_before.append(np.mean(post_number['post_number'].values[:7]))
        posts_after.append(np.mean(post_number['post_number'].values[8:]))

    t, p = stats.wilcoxon(reaction_before, reaction_after)
    print('\nWilcoxon test between the reactions: t =', t, ', p =', p)
    t, p = stats.wilcoxon(share_before, share_after)
    print('\nWilcoxon test between the shares: t =', t, ', p =', p)
    t, p = stats.wilcoxon(comment_before, comment_after)
    print('\nWilcoxon test between the comments: t =', t, ', p =', p)
    t, p = stats.wilcoxon(posts_before, posts_after)
    print('\nWilcoxon test between the number of posts: t =', t, ', p =', p)

    df_reaction['mean'] = df_reaction.mean(axis=1)
    df_share['mean'] = df_share.mean(axis=1)
    df_comment['mean'] = df_comment.mean(axis=1)
    df_post_number['mean'] = df_post_number.mean(axis=1)

    plt.figure(figsize=(10, 7))

    ax = plt.subplot(2, 1, 1)
    plt.plot(df_reaction['mean'], label="Number of reactions per post")
    plt.plot(df_share['mean'], label="Number of shares per post")
    plt.plot(df_comment['mean'], label="Number of comments per post")
    add_layout_details(ax)

    ax = plt.subplot(2, 1, 2)
    plt.plot(df_post_number['mean'], label="Number of posts per day", color="grey")
    add_layout_details(ax)

    plt.tight_layout(pad=3)
    save_figure('figure_5', folder='ip&m', dpi=50)


def save_all_groups_figures(posts_df, repeat_offender_date):

    group_index = 0

    for account_id in posts_df['account_id'].unique():

        if group_index % 10 == 0:
            plt.figure(figsize=(12, 14))

        ax = plt.subplot(5, 2, group_index % 10 + 1)
        
        account_name = posts_df[posts_df['account_id']==account_id].account_name.unique()[0]
        plt.title(account_name, size="x-large")

        plot_one_group(posts_df, account_id, ax)
        plt.axvline(x=np.datetime64(repeat_offender_date[account_name]), 
                    color='C3', linestyle='--', linewidth=2)

        if group_index > 0: 
            ax.get_legend().set_visible(False)

        if (group_index % 10 == 9) | (group_index == posts_df['account_id'].nunique() - 1):
            plt.tight_layout()
            save_figure('supplementary_figure_3_{}'.format(int(group_index / 10) + 1), folder='ip&m', dpi=30)

        group_index += 1


def save_supplementary_table_1():

    df = import_data(folder="self_declared_repeat_offenders", file_name='alledged-repeat-offenders - Feuille 1.csv')
    
    df = df[df['date_in_screenshot'] & df['page_name_in_screenshot'] & df['is_clearly_reduced']]
    df = df[df['group-or-page']=='page']
    df = df.drop_duplicates(subset=['account-url'], keep='first')
    df = df[['repeat-offender-post-url']]

    df_path = os.path.join('.', 'data', 'self_declared_repeat_offenders', 'supplementary_table_1.csv')
    df.to_csv(df_path, index=False)
    print("The supplementary table 1 was saved in the 'self_declared_repeat_offenders' folder.")


if __name__ == "__main__":
    
    posts_df = import_crowdtangle_group_data()
    pages_df = import_data(folder="crowdtangle_list", file_name="self_declared_page_details.csv")
    pages_df['date'] = pd.to_datetime(pages_df['date'])

    save_figure_4(posts_df, pages_df)
    # save_figure_5(posts_df, repeat_offender_date)

    # screenshot_df = import_data(folder="self_declared_repeat_offenders", file_name='posts.csv')
    # print('\nThe average score is {}.'.format(np.nanmean(screenshot_df['score'].values)))
    # print('Only {} posts have a positive score.'.format(len(screenshot_df[screenshot_df['score'] > 0])))

    # save_all_groups_figures(posts_df, repeat_offender_date)
    # # save_supplementary_table_1()