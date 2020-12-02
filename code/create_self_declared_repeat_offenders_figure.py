import os
import datetime
import json
import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import scipy.stats as stats

from create_paper_tables_and_figures import import_data, save_figure


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
    plt.plot(rolling_average_per_day(posts_df_group, 'comment'), label="Number of comments per post")
    plt.plot(rolling_average_per_day(posts_df_group, 'share'), label="Number of shares per post")
    
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


def save_figure_1(posts_df, repeat_offender_date):

    account_name = 'Mark Levin'
    account_id = posts_df[posts_df['account_name']==account_name].account_id.unique()[0]

    plt.figure(figsize=(10, 4))
    ax = plt.subplot()
    
    plt.title(account_name, size="x-large")

    plot_one_group(posts_df, account_id, ax)

    xticks = [np.datetime64('2019-11-01'),
              np.datetime64('2020-01-01'), np.datetime64('2020-03-01'), np.datetime64('2020-05-01'), 
              np.datetime64('2020-07-01'), np.datetime64('2020-09-01'), np.datetime64('2020-11-01'),
              np.datetime64(repeat_offender_date[account_name])]
    plt.xticks(xticks, rotation=30, ha='right')
    plt.gca().get_xticklabels()[-1].set_color('red')

    plt.axvline(x=np.datetime64(repeat_offender_date[account_name]), 
                color='C3', linestyle='--', linewidth=2)

    plt.tight_layout()
    save_figure('sdro_figure_1')


def save_figure_2(posts_df, repeat_offender_date):

    reaction_before = []
    share_before = []
    comment_before = []

    reaction_after = []
    share_after = []
    comment_after = []

    for account_name in posts_df['account_name'].unique():

        posts_df_group = posts_df[posts_df["account_name"] == account_name] 

        posts_df_group_before = posts_df_group[
            (posts_df_group['date'] < datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d')) &
            (posts_df_group['date'] >= datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d') - datetime.timedelta(days=15))
        ]
        posts_df_group_after = posts_df_group[
            (posts_df_group['date'] > datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d')) &
            (posts_df_group['date'] <= datetime.datetime.strptime(repeat_offender_date[account_name], '%Y-%m-%d') + datetime.timedelta(days=15))
        ]

        if ((len(posts_df_group_before['date']) >= 30) & (len(posts_df_group_after['date']) >= 30)):
            reaction_before.append(np.mean(posts_df_group_before['reaction']))
            share_before.append(np.mean(posts_df_group_before['share']))
            comment_before.append(np.mean(posts_df_group_before['comment']))

            reaction_after.append(np.mean(posts_df_group_after['reaction']))
            share_after.append(np.mean(posts_df_group_after['share']))
            comment_after.append(np.mean(posts_df_group_after['comment']))

    fig, ax = plt.subplots(figsize=(6, 3))
    ax.grid(axis="y", zorder=0, linestyle='--')

    width = .25
    labels = ['Reactions', 'Shares', 'Comments']
    x = np.arange(len(labels))
    plt.bar(x - width/2, [np.median(reaction_before), np.median(share_before), np.median(comment_before)], 
                    width, label="The 15 days before the alleged repeat offender date", 
                    color='pink', edgecolor=[.2, .2, .2], zorder=3)
    plt.bar(x + width/2, [np.median(reaction_after), np.median(share_after), np.median(comment_after)], 
                    width, label="The 15 days after the alleged repeat offender date", 
                    color='white', edgecolor=[.2, .2, .2], zorder=3)
    plt.legend(framealpha=1)

    plt.xticks(x, labels)
    ax.tick_params(axis='x', which='both',length=0)
    plt.xlim([-.5, 2.5])

    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)

    fig.tight_layout()
    save_figure('sdro_figure_2')

    t, p = stats.wilcoxon(reaction_before, reaction_after)
    print('\nWilcoxon test between the reactions: t =', t, ', p =', p)
    t, p = stats.wilcoxon(share_before, share_after)
    print('\nWilcoxon test between the shares: t =', t, ', p =', p)
    t, p = stats.wilcoxon(comment_before, comment_after)
    print('\nWilcoxon test between the comments: t =', t, ', p =', p)


def save_all_groups_figures(posts_df, repeat_offender_date):

    group_index = 0

    for account_id in posts_df['account_id'].unique():

        if group_index % 10 == 0:
            plt.figure(figsize=(15, 17))

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
            save_figure('sdro_supplementary_figure_{}'.format(int(group_index / 10) + 1))

        group_index += 1


if __name__ == "__main__":
    collect_date = "2020-12-01"
    posts_df = import_data(folder="data_crowdtangle_group", file_name='posts_group_' + collect_date + '.csv')
    posts_df = clean_post_data(posts_df)
    repeat_offender_date = import_json(folder='self_declared_repeat_offenders', file_name='dates.json')
    save_figure_1(posts_df, repeat_offender_date)
    save_figure_2(posts_df, repeat_offender_date)
    save_all_groups_figures(posts_df, repeat_offender_date)
