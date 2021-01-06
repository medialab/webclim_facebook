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
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize

from utils import import_data, save_figure
from ipm_paper_part_1 import details_temporal_evolution

warnings.filterwarnings("ignore")

stop_words = stopwords.words('english') + ['u', 'also', 'ha']
wnl = WordNetLemmatizer() 


def import_json(folder, file_name):
    data_path = os.path.join('.', 'data', folder, file_name)
    with open(data_path) as json_file:
        data = json.load(json_file)
    return data

def clean_post_data(df):

    clean_df = pd.DataFrame(columns=[
        "account_name", "account_id",
        "date", "share", "comment", "reaction"
    ])

    clean_df['account_name'] = df['account_name'].astype(str)
    clean_df['account_id'] = df['account_id'].astype(int)

    clean_df['date'] = pd.to_datetime(df['date'])

    clean_df['account_id'] = df['account_id'].astype(int)
    clean_df["share"]   = df["actual_share_count"].astype(int)
    clean_df["comment"] = df["actual_comment_count"].astype(int)

    clean_df["reaction"] = df[["actual_like_count", "actual_favorite_count", "actual_love_count",
    "actual_wow_count", "actual_haha_count", "actual_sad_count",
    "actual_angry_count", "actual_thankful_count"]].sum(axis=1).astype(int)

    return clean_df


def rolling_average_per_day(df, column):
    return df.groupby(by=["date"])[column].mean().rolling(window=5, win_type='triang', center=True).mean()


def plot_one_group(posts_df, account_id, ax):
    
    posts_df_group = posts_df[posts_df["account_id"] == account_id] 
    plt.plot(rolling_average_per_day(posts_df_group, 'reaction'), label="Number of reactions per post")
    plt.plot(rolling_average_per_day(posts_df_group, 'share'), label="Number of shares per post")
    plt.plot(rolling_average_per_day(posts_df_group, 'comment'), label="Number of comments per post")
    
    plt.legend()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    plt.xticks(rotation=30, ha='right')
    
    plt.xlim(
        np.datetime64(datetime.datetime.strptime('2019-11-01', '%Y-%m-%d') - datetime.timedelta(days=4)), 
        np.datetime64(datetime.datetime.strptime('2020-11-30', '%Y-%m-%d') + datetime.timedelta(days=4))
    )
    plt.ylim(bottom=0)
    plt.locator_params(axis='y', nbins=3)
    
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.grid(axis="y")


def save_figure_3(posts_df, repeat_offender_date):

    account_name = 'I Love Carbon Dioxide'
    account_id = posts_df[posts_df['account_name']==account_name].account_id.unique()[0]

    plt.figure(figsize=(10, 4))
    ax = plt.subplot()
    
    plt.title(account_name, size="x-large")

    plot_one_group(posts_df, account_id, ax)

    xticks = [np.datetime64('2020-01-01'), np.datetime64('2020-04-01'), np.datetime64('2020-07-01'), 
              np.datetime64('2020-10-01'), np.datetime64(repeat_offender_date[account_name])]
    plt.xticks(xticks, rotation=30, ha='right')
    plt.gca().get_xticklabels()[-1].set_color('red')

    plt.axvline(x=np.datetime64(repeat_offender_date[account_name]), 
                color='C3', linestyle='--', linewidth=2)

    plt.tight_layout()
    save_figure('figure_3', folder='ip&m', dpi=50)


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


def save_figure_4(posts_df, repeat_offender_date):

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
    save_figure('figure_4', folder='ip&m', dpi=50)


def save_supplementary_figure_1(screenshot_df):

    plt.figure(figsize=(10, 4))
    ax = plt.subplot()

    plt.hist(screenshot_df['score'].values, 100, facecolor='grey')
    plt.xlabel("CrowdTangle overperforming scores for the posts sharing the 'reduced distribution' screenshot")
    plt.axvline(x=0, color='k', linestyle='-')

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)

    plt.tight_layout()
    save_figure('supplementary_figure_1', folder='ip&m', dpi=50)

    print('\nThe average score is {}.'.format(np.nanmean(screenshot_df['score'].values)))
    print('Only {} posts have a positive score.'.format(len(screenshot_df[screenshot_df['score'] > 0])))


def save_figure_6(posts_df):

    plt.figure(figsize=(5, 7))

    ax = plt.subplot(3, 1, 1)
    plt.title("self-declared 'repeat offender' accounts", fontsize='x-large')
    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df["date"].value_counts().sort_index(), 
            label="Reactions per post")
    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df["date"].value_counts().sort_index(), 
            label="Shares per post")
    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df["date"].value_counts().sort_index(), 
            label="Comments per post")
    details_temporal_evolution(posts_df, ax)

    ax = plt.subplot(3, 1, 2)
    plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
        label="Posts per day", color=[.2, .2, .2])
    details_temporal_evolution(posts_df, ax)

    ax = plt.subplot(3, 1, 3)
    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Reactions per day")
    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Shares per day")
    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Comments per day")
    details_temporal_evolution(posts_df, ax)

    plt.tight_layout()
    save_figure('figure_6', folder='ip&m', dpi=50)


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
    
    collect_date = "2020-12-01"
    posts_df = import_data(folder="self_declared_repeat_offenders", file_name='posts_group_' + collect_date + '.csv')
    posts_df = clean_post_data(posts_df)
    repeat_offender_date = import_json(folder='self_declared_repeat_offenders', file_name='dates.json')

    save_figure_3(posts_df, repeat_offender_date)
    save_figure_4(posts_df, repeat_offender_date)

    ## minet ct posts-by-id repeat-offender-post-url ./data/self_declared_repeat_offenders/supplementary_table_1.csv > ./data/self_declared_repeat_offenders/posts.csv
    screenshot_df = import_data(folder="self_declared_repeat_offenders", file_name='posts.csv')
    save_supplementary_figure_1(screenshot_df)

    # save_figure_6(posts_df)

    # save_all_groups_figures(posts_df, repeat_offender_date)
    # save_supplementary_table_1()