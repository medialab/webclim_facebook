import sys

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime


def import_data(DATE):

    posts_df = pd.read_csv("./data_crowdtangle_group/posts_group_{}_simple.csv".format(DATE))
    posts_df['date'] = pd.to_datetime(posts_df['date'])
    posts_df = posts_df[posts_df['date'] < datetime.datetime.strptime(DATE, '%Y-%m-%d')]
    if DATE=="2020-07-31":
        posts_df = posts_df[posts_df["account_id"]!=124059257758446] # Usual URL mix-up bug with the CT API

    if DATE=="2020-07-31" or DATE=="2020-07-15" or DATE=="2020-07-24" or DATE=="2020-08-26":
        if DATE=="2020-07-31":
            EXTRACT_DETAILS = "2020-07-27_climate"
            REQUEST_DETAILS = "2020-07-30_climate"
        elif DATE=="2020-07-15" or DATE=="2020-07-24" or DATE=="2020-08-26":
            EXTRACT_DETAILS = "2020-06-29_covid"
            REQUEST_DETAILS = "2020-06-29_covid" 

        url_df = pd.read_csv("./data_sciencefeedback/appearances_{}.csv".format(EXTRACT_DETAILS)) 
        url_df['url'] = url_df['url'].transform(lambda x: x.strip())      

        post_url_df = pd.read_csv("./data_crowdtangle_url/posts_url_{}.csv".format(REQUEST_DETAILS))
        post_url_df = post_url_df.drop_duplicates(subset=["post_url"])
    else:
        url_df = pd.DataFrame()
        post_url_df = pd.DataFrame()

    return posts_df, post_url_df, url_df


def plot_date_markers(post_url_df, url_df, account_id):
    
    post_url_group_df = post_url_df[post_url_df["account_id"]==account_id]
    post_url_group_df = post_url_group_df.sort_values(by='date', ascending=True)\
        .drop_duplicates(subset=['url'], keep='first')

    urls = post_url_group_df["url"].unique().tolist()

    dates_to_plot = []

    for url in urls:
        potential_dates = []
        
        # We consider the date of the Facebook post or posts:
        potential_dates.append(post_url_group_df[post_url_group_df["url"] == url]["date"].values[0])
        # We consider the date of the fact-check:
        potential_dates.append(url_df[url_df['url']==url]["Date of publication"].values[0])
        # TODO: We need to add the date coming from the 'data_sciencefeedback/Rated Archive (06-01-2020 to 07-02-2020).csv' file

        potential_dates = [datetime.datetime.strptime(date, '%Y-%m-%d') for date in potential_dates]
        date_to_plot = np.datetime64(np.max(potential_dates))

        plt.axvline(x=date_to_plot, color='black')
        dates_to_plot.append(date_to_plot)
    
    return dates_to_plot


def plot_repeat_offenders_zone(dates_to_plot):

    area_to_shade = []
    if len(dates_to_plot) > 1:
        area_to_shade = [dates_to_plot[1], dates_to_plot[1] + np.timedelta64(90, 'D')]
        for date in dates_to_plot[2:]:
            if date < area_to_shade[1]:
                area_to_shade[1] = date + np.timedelta64(90, 'D')
    
    plt.axvspan(area_to_shade[0], area_to_shade[1], facecolor='r', alpha=0.2)


def details_figure(title):

    plt.axvline(x=np.datetime64("2020-06-09"), color='grey', linestyle='--')

    plt.legend()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    if (datetime.datetime.strptime(DATE, '%Y-%m-%d') - 
        datetime.datetime.strptime(np.min(posts_df["date"]).strftime("%Y-%m-%d"), '%Y-%m-%d')).days < 365:
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2)) 
    else:
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=4))

    plt.xlim(
        np.datetime64(datetime.datetime.strptime(np.min(posts_df["date"]).strftime("%Y-%m-%d"), '%Y-%m-%d') -
                      datetime.timedelta(days=4)), 
        np.datetime64(datetime.datetime.strptime(DATE, '%Y-%m-%d') + datetime.timedelta(days=4))
    )
    plt.ylim(bottom=0)

    plt.title(title)


def plot_one_group(posts_df, post_url_df, url_df, group_index, plot_also_date_markers=False):
    
    account_id = posts_df['account_id'].unique()[group_index]
    posts_df_group = posts_df[posts_df["account_id"] == account_id]
    
    plt.plot(posts_df_group.groupby(by=["date"])["reaction"].mean(), 
            label="Mean number of reactions per post")

    plt.plot(posts_df_group.groupby(by=["date"])["comment"].mean(), 
            label="Mean number of comments per post")

    if plot_also_date_markers:
        dates_to_plot = plot_date_markers(post_url_df, url_df, account_id)
        plot_repeat_offenders_zone(dates_to_plot)
    
    details_figure(title=posts_df_group['account_name'].unique()[0])


def plot_the_groups_one_by_one(posts_df, post_url_df, url_df, DATE, plot_also_date_markers):

    for group_index in range(posts_df['account_id'].nunique()):

        if group_index % 10 == 0:
            plt.figure(figsize=(12, 15))

        plt.subplot(5, 2, group_index % 10 + 1)
        plot_one_group(posts_df, post_url_df, url_df, group_index, 
                       plot_also_date_markers=plot_also_date_markers)

        if (group_index % 10 == 9) | (group_index == posts_df['account_id'].nunique() - 1):
            plt.tight_layout()
            figure_path = "./figure/group_dynamics_{}_{}.png".format(DATE, int(group_index / 10))
            plt.savefig(figure_path)
            print("The '{}' graph has been saved in the '{}' folder."
                .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


def plot_all_the_groups(posts_df, DATE, plot_only_complete_groups=False):

    if plot_only_complete_groups == True: 
        list_complete_groups_id = []
        for id in posts_df['account_id'].unique():
            posts_df_group = posts_df[posts_df["account_id"] == id]
            if ((np.min(posts_df_group['date']) == np.min(posts_df['date'])) & 
                (np.max(posts_df_group['date']) == datetime.datetime.strptime(DATE, '%Y-%m-%d') - datetime.timedelta(days=1))):
                list_complete_groups_id.append(id)
        posts_df = posts_df[posts_df["account_id"].isin(list_complete_groups_id)]

    plt.figure(figsize=(12, 15))
    plt.subplot(311)

    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of reactions per day")

    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of comments per day")

    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of shares per day")

    details_figure(title="The average daily popularity for the {} Facebook groups/pages"
                       .format(posts_df.account_id.nunique()))

    plt.subplot(312)

    plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
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

    if plot_only_complete_groups == False:
        figure_path = "./figure/average_dynamics_{}.png".format(DATE)
    else:
        figure_path = "./figure/average_dynamics_{}_only_complete_groups.png".format(DATE)
    plt.savefig(figure_path)
    print("The '{}' graph has been saved in the '{}' folder."
            .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


if __name__=="__main__":
    DATE = sys.argv[1]
    posts_df, post_url_df, url_df = import_data(DATE)
    plot_the_groups_one_by_one(posts_df, post_url_df, url_df, DATE, plot_also_date_markers=True)
    plot_all_the_groups(posts_df, DATE, plot_only_complete_groups=False)
    plot_all_the_groups(posts_df, DATE, plot_only_complete_groups=True)
