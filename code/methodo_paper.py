import os
import sys
import warnings

import pandas as pd
import numpy as np
from scipy.stats import ranksums
import datetime
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib_venn import venn3
from fa2 import ForceAtlas2


warnings.filterwarnings("ignore")
pd.options.display.max_colwidth = 300
pd.set_option('display.max_rows', None)


def import_data(folder, file_name):
    data_path = os.path.join(".", 'data', folder, file_name)
    df = pd.read_csv(data_path)
    return df


def save_figure(figure_name, how='matplotlib', A=None, **kwargs):

    figure_path = os.path.join('.', 'figure', 'figure_methodo', figure_name + '.png')
    if how == 'matplotlib':
        plt.savefig(figure_path, **kwargs)
    elif how == 'graphviz':
        A.draw(figure_path)

    print('\n\n' + figure_name.upper())
    print("The '{}' figure has been saved in the '{}' folder."\
        .format(figure_path.split('/')[-1], figure_path.split('/')[-2]))


def save_table(df, table_name):

    table_path = os.path.join('.', 'figure', 'figure_methodo', table_name + '.csv')
    df.to_csv(table_path, index=False, header=True)

    print('\n\n' + table_name.upper())
    print("The '{}' table has been saved in the '{}' folder."\
        .format(table_path.split('/')[-1], table_path.split('/')[-2]))


def print_table_1(url_df):

    print()
    print(url_df["scientific_topic"].value_counts(dropna=False))

    print('\nThere are {} domain names.'.format(url_df["domain_name"].nunique()))

    table_1 = []
    for topic in url_df["scientific_topic"].unique():

        url_df_temp = url_df[url_df["scientific_topic"]==topic]
        url_df_temp = url_df_temp['domain_name'].value_counts(dropna=False).nlargest(10).to_frame()
        url_df_temp['top 10 ' + topic] = url_df_temp.index + ' (' + url_df_temp['domain_name'].astype(str) + ')'
        table_1.append(url_df_temp['top 10 ' + topic].reset_index(drop=True))
        
    table_1 = pd.concat(table_1, axis=1, sort=False)
    save_table(table_1, 'table_1')


def create_venn_diagram(df, topic_color, column_name, name):

    subsets = []
    for topic in df["scientific_topic"].unique():
        df_temp = df[df["scientific_topic"]==topic]
        subsets.append(set(df_temp[column_name].unique()))

    plt.figure()

    venn3(subsets=subsets, 
          set_labels=('health', 'climate', 'covid'),
          set_colors=(topic_color['health'], topic_color['climate'], topic_color['covid']),
          alpha=1)

    save_figure(name)

    if name == 'figure_1':
        print('\n\nLIST INTERSECTION DOMAIN NAMES')
        l = list(subsets[0] & subsets[1] & subsets[2])
        for ele in sorted(l): 
            print(ele, end=', ')


def save_figure_1(url_df, topic_color):
    create_venn_diagram(url_df, topic_color, 'domain_name', 'figure_1')


def clean_crowdtangle_url_data(post_url_df, url_df):

    post_url_df = post_url_df[post_url_df["platform"] == "Facebook"]
    post_url_df = post_url_df.dropna(subset=['account_id', 'url'])

    post_url_df = post_url_df.sort_values(by=['datetime'], ascending=True)
    post_url_df = post_url_df.drop_duplicates(subset=['account_id', 'url'], keep='first')

    post_url_df = post_url_df[['url', 'account_id', 'account_name', 'account_subscriber_count', 'date']]

    post_url_df = post_url_df.merge(url_df[['url', 'scientific_topic']], on='url', how='left')

    return post_url_df


def print_table_2(post_url_df, url_df):

    print('\n\n\nThere are {} Facebook accounts.'.format(post_url_df["account_id"].nunique()))
    table_2 = []

    for topic in post_url_df["scientific_topic"].unique():
        post_url_df_temp = post_url_df[post_url_df["scientific_topic"]==topic]
        top_10_temp = post_url_df_temp['account_id'].value_counts(dropna=False).nlargest(10)\
            .rename_axis('account_id').to_frame('nb_fake_news_share')
        top_10_temp = top_10_temp.reset_index()
        top_10_temp = top_10_temp.merge(post_url_df[['account_id', 'account_name']].drop_duplicates(), 
                                        on='account_id', how='left')
        top_10_temp['top 10 ' + topic] = top_10_temp['account_name'] + ' (' + top_10_temp['nb_fake_news_share'].astype(str) + ')'
        table_2.append(top_10_temp['top 10 ' + topic].reset_index(drop=True))

    table_2 = pd.concat(table_2, axis=1, sort=False)
    save_table(table_2, 'table_2')


def save_figure_2(post_url_df, topic_color):
    create_venn_diagram(post_url_df,  topic_color, 'account_id', 'figure_2')


def save_figure_3(post_url_df, url_df, topic_color):

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
            color=list(topic_color.values())[i]
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


def color_gradient(ratio_climate, ratio_health, topic_color):
    climate_color = np.array(mpl.colors.to_rgb(topic_color["climate"]))
    health_color = np.array(mpl.colors.to_rgb(topic_color["health"]))
    covid_color = np.array(mpl.colors.to_rgb(topic_color["covid"]))

    gradient_color =  (ratio_climate * climate_color + ratio_health * health_color + 
                       (1 - ratio_climate - ratio_health) * covid_color)
    return mpl.colors.to_hex(gradient_color)


def save_figure_4(post_url_df, topic_color):

    vc = post_url_df['account_id'].value_counts()
    post_url_df = post_url_df[post_url_df['account_id'].isin(vc[vc > 3].index)]

    bipartite_graph = nx.Graph()

    fb_group_df = post_url_df.drop_duplicates(subset=['account_id'])\
        [['account_id', 'account_name', 'account_subscriber_count']]

    list_topic = post_url_df.groupby('account_id')['scientific_topic'].apply(list)\
        .to_frame().reset_index()
    list_topic['nb_fake_news_shared'] = list_topic['scientific_topic'].apply(lambda x:len(x))

    list_topic['covid'] = list_topic['scientific_topic'].apply(lambda x:x.count("covid"))
    list_topic['climate'] = list_topic['scientific_topic'].apply(lambda x:x.count("climate"))
    list_topic['health'] = list_topic['scientific_topic'].apply(lambda x:x.count("health"))
    list_topic['main_topic'] = list_topic[['covid', 'climate', 'health']].idxmax(axis=1)

    list_topic['ratio_climate'] = list_topic['climate'] / list_topic['nb_fake_news_shared']
    list_topic['ratio_health'] = list_topic['health'] / list_topic['nb_fake_news_shared']

    fb_group_df = fb_group_df.merge(list_topic[['account_id', 'ratio_climate', 'ratio_health']], 
                                    on='account_id', how='left')

    print('\nThere are {} Facebook accounts sharing more than 3 articles.'.format(len(fb_group_df)))

    for _, row in fb_group_df.iterrows():
        bipartite_graph.add_node(int(row['account_id']),
                                label=row['account_name'],
                                subscriber_number=row['account_subscriber_count'],
                                ratio_climate=row['ratio_climate'],
                                ratio_health=row['ratio_health']
                                )

    bipartite_graph.add_nodes_from(post_url_df["url"].tolist())

    bipartite_graph.add_edges_from(list(post_url_df[['account_id', 'url']]\
                                   .itertuples(index=False, name=None)))

    G = nx.algorithms.bipartite.projected_graph(
        bipartite_graph, fb_group_df['account_id'].unique().tolist()
    )

    forceatlas2 = ForceAtlas2(
        outboundAttractionDistribution=False,
        linLogMode=False,
        adjustSizes=False,
        edgeWeightInfluence=0,
        jitterTolerance=1.0,
        barnesHutOptimize=False,
        barnesHutTheta=0.5,
        multiThreaded=False,
        scalingRatio=10,
        strongGravityMode=True,
        gravity=0.05
    )

    pos = forceatlas2.forceatlas2_networkx_layout(G, pos=None, iterations=2000)

    plt.figure(figsize=(15, 12))

    node_size = [data["subscriber_number"] / 10000 + 10 for v, data in G.nodes(data=True)]

    node_color = [color_gradient(data["ratio_climate"], data["ratio_health"], topic_color) 
                  for v, data in G.nodes(data=True)]

    nx.draw_networkx_nodes(G, pos=pos, node_color=node_color, node_size=node_size)
    nx.draw_networkx_edges(G, pos=pos, alpha=0.2, edge_color='lightgrey')

    nodes_to_label = fb_group_df.sort_values(by='account_subscriber_count', ascending=False).head(15)\
                        ['account_id'].tolist()
    pos_to_label = {node: pos[node] for node in nodes_to_label}
    labels = {node: fb_group_df[fb_group_df['account_id']==node].iloc[0]['account_name'] 
            for node in nodes_to_label}

    nx.draw_networkx_labels(
        G, labels=labels, font_color='black', pos=pos_to_label
    )

    plt.axis("off")
    save_figure('figure_4')


if __name__ == "__main__":

    DATE = sys.argv[1] if len(sys.argv) >= 2 else "2020-08-27"

    if DATE == "2020-08-27":
        DATE_URL_REQUEST = "2020-08-31"

    topic_color = {
        "health": "mediumseagreen",
        "covid": "salmon",
        "climate": "dodgerblue"
    }

    url_df = import_data(folder="sciencefeedback", file_name="appearances_" + DATE + "_.csv")
    print_table_1(url_df)
    save_figure_1(url_df, topic_color)

    post_url_df = import_data(folder="crowdtangle_url", file_name="posts_url_" + DATE_URL_REQUEST + "_.csv")
    post_url_df = clean_crowdtangle_url_data(post_url_df, url_df)
    print_table_2(post_url_df, url_df)
    save_figure_2(post_url_df, topic_color)
    save_figure_3(post_url_df, url_df, topic_color)
    save_figure_4(post_url_df, topic_color)

