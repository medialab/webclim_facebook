import sys

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


def import_data(DATE):

    posts_df = pd.read_csv("./data_crowdtangle_group/posts_group_{}_simple.csv".format(DATE))
    posts_df['date'] = pd.to_datetime(posts_df['date'])
    posts_df = posts_df[posts_df['date'] <= "2020-07-14"]

    return posts_df


def details_figure(title):

    plt.axvline(x=np.datetime64("2020-06-09"), color='grey', linestyle='--')

    plt.legend()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2)) 

    plt.xlim(np.datetime64('2019-08-26'), np.datetime64('2020-07-18'))
    plt.ylim(bottom=0)

    plt.title(title)


def plot_one_group(posts_df, group_index):
    
    group_id = posts_df['account_id'].unique()[group_index]
    posts_df_group = posts_df[posts_df["account_id"] == group_id]
    
    plt.plot(posts_df_group.groupby(by=["date"])["reaction"].mean(), 
            label="Mean number of reactions per post")

    plt.plot(posts_df_group.groupby(by=["date"])["comment"].mean(), 
            label="Mean number of comments per post")
    
    details_figure(title=posts_df_group['account_name'].unique()[0])


def plot_the_groups_one_by_one(posts_df, DATE):

    for group_index in range(posts_df['account_id'].nunique()):

        if group_index % 10 == 0:
            plt.figure(figsize=(12, 15))

        plt.subplot(5, 2, group_index % 10 + 1)
        plot_one_group(posts_df, group_index)

        if (group_index % 10 == 9) | (group_index == posts_df['account_id'].nunique() - 1):
            plt.tight_layout()
            figure_path = "./figure/group_dynamics_{}_{}.png".format(DATE, int(group_index / 10))
            plt.savefig(figure_path)
            print("The '{}' graph has been saved in the '{}' folder."
                .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


def plot_all_the_groups(posts_df, DATE):

    plt.figure(figsize=(12, 15))
    plt.subplot(311)

    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.account_id.nunique(), 
            label="Mean number of reactions per day")

    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.account_id.nunique(), 
            label="Mean number of comments per day")

    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.account_id.nunique(), 
            label="Mean number of shares per day")

    details_figure(title="The average daily popularity for the {} Facebook groups/pages"
                       .format(posts_df.account_id.nunique()))

    plt.subplot(312)

    plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.account_id.nunique(), 
        label="Mean number of posts per day", color="red")

    details_figure(title="The average daily posts for the {} Facebook groups/pages"
                       .format(posts_df.account_id.nunique()))

    plt.subplot(313)

    plt.plot(posts_df.groupby(by=["date"])["reaction"].mean(), 
            label="Mean number of reactions per post")

    plt.plot(posts_df.groupby(by=["date"])["comment"].mean(), 
            label="Mean number of comments per post")

    plt.plot(posts_df.groupby(by=["date"])["share"].mean(), 
            label="Mean number of shares per post")

    details_figure(title="The average popularity per post for the {} Facebook groups/pages"
                       .format(posts_df.account_id.nunique()))

    plt.tight_layout()

    figure_path = "./figure/average_dynamics_{}.png".format(DATE)
    plt.savefig(figure_path)
    print("The '{}' graph has been saved in the '{}' folder."
            .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


if __name__=="__main__":
    DATE = sys.argv[1]
    posts_df = import_data(DATE)
    plot_the_groups_one_by_one(posts_df, DATE)
    plot_all_the_groups(posts_df, DATE)
