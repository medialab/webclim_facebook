import os
import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from create_paper_tables_and_figures import import_data, save_figure

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


def plot_one_group(posts_df, account_id, reduced_date, ax):
    
    posts_df_group = posts_df[posts_df["account_id"] == account_id] 
    plt.plot(rolling_average_per_day(posts_df_group, 'reaction'), label="Number of reactions per post")
    plt.plot(rolling_average_per_day(posts_df_group, 'comment'), label="Number of comments per post")
    plt.plot(rolling_average_per_day(posts_df_group, 'share'), label="Number of shares per post")
    
    plt.axvline(x=np.datetime64(reduced_date), color='C3', linestyle='--', linewidth=2)

    plt.legend()

    xlabels = [np.datetime64('2019-01-01'), np.datetime64('2019-03-01'), np.datetime64('2019-05-01'), 
               np.datetime64('2019-07-01'), np.datetime64('2019-09-01'), np.datetime64('2019-11-01'),
               np.datetime64('2020-01-01'), np.datetime64('2020-03-01'), np.datetime64('2020-05-01'), 
               np.datetime64('2020-07-01'), np.datetime64('2020-09-01'), np.datetime64('2020-11-01'),
               np.datetime64(reduced_date)]
    if account_id == 111077570271805:
        xlabels.pop(11)
    plt.xticks(xlabels, rotation=30, ha='right')
    plt.gca().get_xticklabels()[-1].set_color('red')
    
    plt.xlim(
        np.datetime64(datetime.datetime.strptime('2019-01-01', '%Y-%m-%d') - datetime.timedelta(days=4)), 
        np.datetime64(datetime.datetime.strptime('2020-11-30', '%Y-%m-%d') + datetime.timedelta(days=4))
    )
    plt.ylim(bottom=0)
    
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.grid(axis="y")


def save_blog_figure(posts_df):

    plt.figure(figsize=(9, 13))
    group_index = 0

    for account_id in [311190048935167, 368557930146199, 16307558831, 111077570271805]:

        ax = plt.subplot(4, 1, group_index + 1)
        
        account_name = posts_df[posts_df['account_id']==account_id].account_name.unique()[0]
        plt.title(account_name, size="x-large")
        
        if account_name == '100 Percent FED Up':
            reduced_date = '2020-07-31'
            plt.yticks([2500, 5000])
            plt.ylim([0, 6000])
        elif account_name == 'Tucker Carlson Tonight':
            reduced_date = '2020-09-24'
            plt.yticks([50000, 100000])
        elif account_name == 'Mark Levin':
            reduced_date = '2020-10-05'
            plt.yticks([10000, 20000])
        elif account_name == 'Wendy Bell Radio':
            reduced_date = '2020-11-09'

        plot_one_group(posts_df, account_id, reduced_date, ax)
        
        if group_index > 0: 
            ax.get_legend().set_visible(False)
        group_index += 1
                
    plt.tight_layout(pad=4.0)
    save_figure('figure_blog_post')


if __name__ == "__main__":
    #collect_date = "2020-11-17"
    collect_date = "2020-11-23"
    posts_df = import_data(folder="data_crowdtangle_group", file_name='posts_group_' + collect_date + '.csv')
    posts_df = clean_post_data(posts_df)
    save_blog_figure(posts_df)
