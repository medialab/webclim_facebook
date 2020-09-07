import os
import sys

import pandas as pd
import numpy as np
from scipy.stats import ranksums
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib_venn import venn3


pd.options.display.max_colwidth = 300


def import_data(folder, file_name):
    data_path = os.path.join(".", folder, file_name)
    df = pd.read_csv(data_path)
    return df


def save_figure(figure_name):

    figure_path = os.path.join('.', 'figure', figure_name + '.png')
    plt.savefig(figure_path)

    print('\n\n' + figure_name.upper())
    print("The '{}' figure has been saved in the '{}' folder."\
        .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


def print_table_1(url_df):

    print()
    print(url_df["scientific_topic"].value_counts(dropna=False))

    print('\nThere are {} domain names.'.format(url_df["domain_name"].nunique()))

    print('\nTABLE 1')
    for topic in url_df["scientific_topic"].unique():
        print(topic.upper())
        url_df_temp = url_df[url_df["scientific_topic"]==topic]
        print(url_df_temp['domain_name'].value_counts(dropna=False).nlargest(10))
        print()


def save_figure_1(url_df, DATE):

    # Create a list with the 3 domain names sets
    domain_name_subsets = []
    for topic in url_df["scientific_topic"].unique():
        url_df_temp = url_df[url_df["scientific_topic"]==topic]
        domain_name_subsets.append(set(url_df_temp["domain_name"].unique()))

    # Save the Venn diagram figure
    plt.figure()

    v = venn3(subsets=domain_name_subsets, 
            set_labels=('health', 'climate', 'covid'),
            set_colors=([1, 1, 0.6, 1], [0.4, 0.4, 1, 1], [1, 0.4, 0.4, 1]),
            alpha=1)

    v.get_patch_by_id('110').set_color([0.5, 1, 0.5, 1])
    v.get_patch_by_id('101').set_color([1, 0.75, 0.5, 1])
    v.get_patch_by_id('011').set_color([1, 0.4, 1, 1])
    v.get_patch_by_id('111').set_color([0.95, 0.95, 0.95, 1])

    save_figure('figure_1')

    print('\n\nLIST INTERSECTION DOMAIN NAMES')
    l = list(domain_name_subsets[0] & domain_name_subsets[1] & domain_name_subsets[2])
    for ele in sorted(l): 
        print(ele, end=', ')


def clean_crowdtangle_url_data(post_url_df):

    post_url_df = post_url_df[post_url_df["platform"] == "Facebook"]
    post_url_df = post_url_df.dropna(subset=['account_id', 'url'])
    post_url_df = post_url_df.drop_duplicates(subset=['account_id', 'url'], keep='first')
    post_url_df = post_url_df[['url', 'account_id', 'account_name']]

    post_url_df = post_url_df.merge(url_df[['url', 'scientific_topic']], on='url', how='left')

    return post_url_df


def print_table_2(post_url_df, url_df):
    print('\n\n\nThere are {} Facebook accounts.'.format(post_url_df["account_id"].nunique()))

    print('\nTABLE 2')
    for topic in post_url_df["scientific_topic"].unique():
        print(topic.upper())
        post_url_df_temp = post_url_df[post_url_df["scientific_topic"]==topic]
        top_10_temp = post_url_df_temp['account_id'].value_counts(dropna=False).nlargest(10)\
            .rename_axis('account_id').to_frame('nb_fake_news_share')
        top_10_temp = top_10_temp.reset_index()
        top_10_temp = top_10_temp.merge(post_url_df[['account_id', 'account_name']].drop_duplicates(), 
                                        on='account_id', how='left')
        top_10_temp.index = top_10_temp['account_name']
        top_10_temp = top_10_temp[['nb_fake_news_share']]
        print(top_10_temp)
        print()

    return


def save_figure_2(post_url_df, DATE):

    # Create a list with the 3 domain names sets
    accounts_subsets = []
    for topic in url_df["scientific_topic"].unique():
        post_url_df_temp = post_url_df[post_url_df["scientific_topic"]==topic]
        accounts_subsets.append(set(post_url_df_temp["account_id"].unique()))

    # Save the Venn diagram figure
    plt.figure()

    v = venn3(subsets=accounts_subsets, 
            set_labels=('health', 'climate', 'covid'),
            set_colors=([1, 1, 0.6, 1], [0.4, 0.4, 1, 1], [1, 0.4, 0.4, 1]),
            alpha=1)

    v.get_patch_by_id('110').set_color([0.5, 1, 0.5, 1])
    v.get_patch_by_id('101').set_color([1, 0.75, 0.5, 1])
    v.get_patch_by_id('011').set_color([1, 0.4, 1, 1])
    v.get_patch_by_id('111').set_color([0.95, 0.95, 0.95, 1])

    save_figure('figure_2')


def save_figure_3(post_url_df, url_df, DATE):

    url_share_df = post_url_df['url'].value_counts().rename_axis('url').to_frame('nb_shares')

    add_zero_shares_url = pd.DataFrame(
        {'nb_shares': [0] * len(set(url_df["url"]) - set(post_url_df['url']))},
        index = list(set(url_df["url"]) - set(post_url_df['url']))
    )

    print('\nThere are {} URLs.'.format(url_df["url"].nunique()))
    print('{} URLs are never shared on Facebook ({} %).'\
        .format(len(add_zero_shares_url), int(np.round(100 * len(add_zero_shares_url)/url_df["url"].nunique()))))

    url_share_df = pd.concat([url_share_df, add_zero_shares_url])

    url_share_df['url'] = url_share_df.index
    url_share_df = url_share_df.merge(url_df[['url', 'scientific_topic']], on='url', how='left')

    colors = ['y', 'r', 'b']

    plt.figure(figsize=(6, 6))

    nb_shares_per_topic = []

    for i in range(url_share_df["scientific_topic"].nunique()):
        topic = url_share_df["scientific_topic"].unique()[i]
        ax = plt.subplot(3, 1, i+1)

        nb_shares_temp = url_share_df[url_share_df["scientific_topic"]==topic][['nb_shares']].values
        nb_shares_per_topic.append(nb_shares_temp)

        plt.hist(
            nb_shares_temp,
            bins=np.arange(0, 100, 1),
            color=colors[i]
        )
        
        mean_temp = np.mean(nb_shares_temp)
        if i == 1:
            height = [100, 130, 170]
        else:
            height = [50, 75, 100]
        plt.plot([mean_temp, mean_temp], [0, height[0]], 'k--')
        plt.text(mean_temp, height[2], 'mean:', horizontalalignment='center', verticalalignment='center')
        plt.text(mean_temp, height[1], str(np.round(mean_temp, 1)), horizontalalignment='center', verticalalignment='center')
        
        plt.text(0.9, 0.85, topic, size=14, horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        if i == 2:
            plt.xlabel('Number of Facebook accounts sharing each URL')
        plt.xlim([0, 100])

    plt.tight_layout()
        
    save_figure('figure_3')

    print("\nWilcoxon rank-test between health and covid:")
    print(ranksums(nb_shares_per_topic[0], nb_shares_per_topic[1]))

    print("\nWilcoxon rank-test between covid and climate:")
    print(ranksums(nb_shares_per_topic[1], nb_shares_per_topic[2]))   

    print("\nWilcoxon rank-test between health and climate:")
    print(ranksums(nb_shares_per_topic[0], nb_shares_per_topic[2]))


def details_temporal_evolution(posts_df):

    plt.axvline(x=np.datetime64("2020-06-09"), color='black', linestyle='--', linewidth=1)

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


def plot_temporal_evolution(posts_df):

    plt.figure(figsize=(10, 8))
    plt.subplot(211)

    plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of reactions per day")

    plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of shares per day")

    plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
            label="Mean number of comments per day")

    details_temporal_evolution(posts_df)
    plt.title("The temporal evolution of the {} Facebook accounts spreading misinformation".format(posts_df["account_id"].nunique()))

    plt.subplot(212)

    plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.groupby(by=["date"])["account_id"].nunique(), 
        label="Mean number of posts per day", color="grey")

    details_temporal_evolution(posts_df)

    plt.tight_layout()


def save_figure_6(posts_df):

    plot_temporal_evolution(posts_df)
    save_figure('figure_6')


def save_supplementary_figure_1(posts_df):

    list_complete_groups_id = []
    for id in posts_df['account_id'].unique():
        posts_df_group = posts_df[posts_df["account_id"] == id]
        if ((np.min(posts_df_group['date']) == np.min(posts_df['date'])) & 
            (np.max(posts_df_group['date']) == datetime.datetime.strptime(DATE, '%Y-%m-%d') - datetime.timedelta(days=1))):
            list_complete_groups_id.append(id)
    posts_df_temp = posts_df[posts_df["account_id"].isin(list_complete_groups_id)]

    plot_temporal_evolution(posts_df_temp)

    save_figure('supplementary_figure_1')


if __name__ == "__main__":

    DATE = sys.argv[1] if len(sys.argv) >= 2 else "2020-08-27"

    if DATE == "2020-08-27":
        DATE_URL_REQUEST = "2020-08-31"
        DATE_GROUP_REQUEST = "2020-09-01"

    # url_df = import_data(folder="data_sciencefeedback", file_name="appearances_" + DATE + "_.csv")
    # print_table_1(url_df)
    # save_figure_1(url_df, DATE)

    # post_url_df = import_data(folder="data_crowdtangle_url", file_name="posts_url_" + DATE_URL_REQUEST + "_.csv")
    # post_url_df = clean_crowdtangle_url_data(post_url_df)
    # print_table_2(post_url_df, url_df)
    # save_figure_2(post_url_df, DATE)
    # save_figure_3(post_url_df, url_df, DATE)

    posts_fake_group_df = import_data(folder="data_crowdtangle_group", file_name="posts_fake_group.csv")
    posts_fake_page_df = import_data(folder="data_crowdtangle_group", file_name="posts_fake_page.csv")
    posts_fake_df = pd.concat([posts_fake_group_df, posts_fake_page_df])
    posts_fake_df['date'] = pd.to_datetime(posts_fake_df['date'])
    posts_fake_df = posts_fake_df[posts_fake_df['date'] < datetime.datetime.strptime(DATE, '%Y-%m-%d')]

    save_figure_6(posts_fake_df)
    save_supplementary_figure_1(posts_fake_df)