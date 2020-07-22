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


def plot_figure(posts_df, DATE):

    plt.figure(figsize=(12, 15))
    plt.subplot(311)

    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.account_id.nunique(), 
            label="Mean number of reactions per day")

    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.account_id.nunique(), 
            label="Mean number of comments per day")

    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.account_id.nunique(), 
            label="Mean number of shares per day")

    details_figure(title="The average daily popularity for the {} Facebook groups"
                       .format(posts_df.account_id.nunique()))

    plt.subplot(312)

    plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.account_id.nunique(), 
        label="Mean number of posts per day", color="red")

    details_figure(title="The average daily posts for the {} Facebook groups"
                       .format(posts_df.account_id.nunique()))

    plt.subplot(313)

    plt.plot(posts_df.groupby(by=["date"])["reaction"].mean(), 
            label="Mean number of reactions per post")

    plt.plot(posts_df.groupby(by=["date"])["comment"].mean(), 
            label="Mean number of comments per post")

    plt.plot(posts_df.groupby(by=["date"])["share"].mean(), 
            label="Mean number of shares per post")

    details_figure(title="The average popularity per post for the {} Facebook groups"
                       .format(posts_df.account_id.nunique()))

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
