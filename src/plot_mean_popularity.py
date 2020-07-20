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

    plt.legend()

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2)) 

    plt.xlim(np.datetime64('2019-08-26'), np.datetime64('2020-07-18'))
    plt.ylim(bottom=0)

    plt.title("The average " + title + " for the {} Facebook groups".format(posts_df.account_id.nunique()))


def plot_figure(posts_df, DATE):

    plt.figure(figsize=(12, 10))
    plt.subplot(211)

    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.account_id.nunique(), 
            label="Mean number of reactions per day")

    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.account_id.nunique(), 
            label="Mean number of comments per day")

    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.account_id.nunique(), 
            label="Mean number of shares per day")

    details_figure(title="daily popularity")

    plt.subplot(212)

    plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.account_id.nunique(), 
        label="Mean number of posts per day", color="red")

    details_figure(title="daily posts")

    plt.tight_layout()

    figure_path = "./figure/average_dynamics_{}.png".format(DATE)
    plt.savefig(figure_path)
    print("The '{}' graph has been saved in the '{}' folder."
            .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))

    plt.show()


if __name__=="__main__":
    DATE = "2020-07-15"
    posts_df = import_data(DATE)
    plot_figure(posts_df, DATE)
