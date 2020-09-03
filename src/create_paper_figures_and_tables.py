import os
import sys

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib_venn import venn3


def import_clean_science_feedback_data(DATE):
    url_path = os.path.join(".", "data_sciencefeedback", "appearances_" + DATE + "_.csv")
    url_df = pd.read_csv(url_path)
    return url_df


def print_table_1(url_df):

    # Print the top 10 domain names for each topic
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
    print('\n\n')


if __name__ == "__main__":

    DATE = sys.argv[1]

    url_df = import_clean_science_feedback_data(DATE)
    print_table_1(url_df)
    save_figure_1(url_df, DATE)