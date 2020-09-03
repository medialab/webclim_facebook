import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3


def import_data(folder, file_name):
    data_path = os.path.join(".", folder, file_name)
    df = pd.read_csv(data_path)
    return df


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

    diagram_path = os.path.join('.', 'figure', 'venn_diagram_domain_names_' + DATE + ".png")
    plt.savefig(diagram_path)

    print('\nFIGURE 1')
    print("The '{}' figure has been saved in the '{}' folder."\
        .format(diagram_path.split('/')[-1], diagram_path.split('/')[-2]))

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
        print(post_url_df_temp['account_name'].value_counts(dropna=False).nlargest(10))
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

    diagram_path = os.path.join('.', 'figure', 'venn_diagram_facebook_accounts_' + DATE + ".png")
    plt.savefig(diagram_path)

    print('\nFIGURE 2')
    print("The '{}' figure has been saved in the '{}' folder."\
        .format(diagram_path.split('/')[-1], diagram_path.split('/')[-2]))


if __name__ == "__main__":

    DATE = sys.argv[1] if len(sys.argv) >= 2 else "2020-08-27"

    if DATE == "2020-08-27":
        DATE_URL_REQUEST = "2020-08-31"
        DATE_GROUP_REQUEST = "2020-09-01"

    url_df = import_data(folder="data_sciencefeedback", file_name="appearances_" + DATE + "_.csv")
    print_table_1(url_df)
    save_figure_1(url_df, DATE)

    post_url_df = import_data(folder="data_crowdtangle_url", file_name="posts_url_" + DATE_URL_REQUEST + "_.csv")
    post_url_df = clean_crowdtangle_url_data(post_url_df)
    print_table_2(post_url_df, url_df)
    save_figure_2(post_url_df, DATE)