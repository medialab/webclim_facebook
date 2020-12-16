import pandas as pd
import numpy as np

from utils import import_data, keep_only_one_year_data, clean_crowdtangle_url_data


def filter_accounts_sharing_less_than_x_fake_news(df, x):
    value_count = df.drop_duplicates(subset=['account_id', 'url'], keep='first')['account_id'].value_counts()
    df_filtered = df[df['account_id'].isin(value_count[value_count >= x].index)]
    return df_filtered


def print_table_1(df_before, df_after):
    
    print('\n\nTABLE 1')

    df_before_filtered = filter_accounts_sharing_less_than_x_fake_news(df_before, x=10)
    print('\nThere are {} Facebook accounts sharing more than 10 fake news in the June data.'\
        .format(df_before_filtered.account_id.nunique()))

    list_qanon_before = [name for name in list(df_before_filtered.account_name.value_counts().index) if 'Q' in name]
    print('The list of the {} QAnon related accounts in the June data:'.format(len(list_qanon_before)))
    print(df_before_filtered[df_before_filtered['account_name'].isin(list_qanon_before)]\
        [['account_name', 'account_subscriber_count']].drop_duplicates()\
        .sort_values(by='account_subscriber_count', ascending=False).to_string(index=False))
    print('Total number of follower: {}'.format(np.sum(df_before_filtered[df_before_filtered['account_name'].isin(list_qanon_before)]\
        [['account_name', 'account_subscriber_count']].drop_duplicates()[['account_subscriber_count']].values)))


    df_after_filtered = filter_accounts_sharing_less_than_x_fake_news(df_after, x=10)
    print('\nThere are {} Facebook accounts sharing more than 10 fake news in the August data.'\
        .format(df_after_filtered.account_id.nunique()))

    list_qanon_after = [name for name in list(df_after_filtered.account_name.value_counts().index) if 'Q' in name]
    print('The list of the {} QAnon related accounts in the Augsut data:'.format(len(list_qanon_after)))
    print(df_after_filtered[df_after_filtered['account_name'].isin(list_qanon_after)]\
        [['account_name', 'account_subscriber_count']].drop_duplicates()\
        .sort_values(by='account_subscriber_count', ascending=False).to_string(index=False))
    print('Total number of follower: {}'.format(np.sum(df_after_filtered[df_after_filtered['account_name'].isin(list_qanon_after)]\
        [['account_name', 'account_subscriber_count']].drop_duplicates()[['account_subscriber_count']].values)))


def print_table_2(df_before, df_after):

    print('\n\nTABLE 2')

    df_before_filtered = filter_accounts_sharing_less_than_x_fake_news(df_before, x=3)
    print('\nThere are {} Facebook accounts sharing more than 3 fake news in the June data.'\
        .format(df_before_filtered.account_id.nunique()))

    list_qanon_before = [name for name in list(df_before_filtered.account_name.value_counts().index) if 'Q' in name]
    accounts_to_remove_before = [
        "Vương Nhất Bác 王一博 - UNIQ's Wang Yibo 1st Vietnamese Fanpage",
        'QUESTION EVERYTHING... EVERYWHERE',
        'QuantumEquilibrium ~ The Truth State',
        '@STOP 5 G MONTRÉAL/QUÉBEC',
        'AMERICANS Against Excessive Quarantine!',
        'Questioning Global Warming',
        'QUESTION EVERYTHING',
        'Rastos Quimicos Portugal//Chemtrail Activism',
        'Natural And Quodesh',
        'STOP 5G Val-David. Laurentides et autres circonscriptions du Québec',
        'Rockcastle County C.V.Q.R.G',
        'Info Pro-Trump  Québec'
    ]
    list_qanon_before = [x for x in list_qanon_before if x not in accounts_to_remove_before]

    print('There are {} accounts with Q in their names in the June data.'.format(len(list_qanon_before)))
    print('Total number of follower: {}'.format(np.sum(df_before_filtered[df_before_filtered['account_name'].isin(list_qanon_before)]\
        [['account_name', 'account_subscriber_count']].drop_duplicates()[['account_subscriber_count']].values)))


    df_after_filtered = filter_accounts_sharing_less_than_x_fake_news(df_after, x=3)
    print('\nThere are {} Facebook accounts sharing more than 3 fake news in the August data.'\
        .format(df_after_filtered.account_id.nunique()))

    list_qanon_after = [name for name in list(df_after_filtered.account_name.value_counts().index) if 'Q' in name]
    accounts_to_remove_after = [
        'QUESTION EVERYTHING... EVERYWHERE',
        'AMERICANS Against Excessive Quarantine!',
        'Info Pro-Trump  Québec',
        'Médias Alternatifs Québecois',
        'Wisconsinites Against Excessive Quarantine',
        'Minnesotans Against Excessive Quarantine',
        'Venner, der synes godt om Question Everything',
        'Spiritual Awakening, Quantum Physics, Aliens & The 5th Dimension',
        'Canadians Against Excessive Quarantine',
        'PRQBUĐENI HRVATSKA',
        'Quotes of Life',
        'QUESTION EVERYTHING',
        'Rastos Quimicos Portugal//Chemtrail Activism',
        '@STOP 5 G MONTRÉAL/QUÉBEC',
        'QuantumEquilibrium ~ The Truth State',
        'STOP 5G Val-David. Laurentides et autres circonscriptions du Québec',
        'Rockcastle County C.V.Q.R.G'
    ]
    list_qanon_after = [x for x in list_qanon_after if x not in accounts_to_remove_after]

    print('There are {} accounts with Q in their names in the August data.'.format(len(list_qanon_after)))
    print('Total number of follower: {}'.format(np.sum(df_after_filtered[df_after_filtered['account_name'].isin(list_qanon_after)]\
        [['account_name', 'account_subscriber_count']].drop_duplicates()[['account_subscriber_count']].values)))


if __name__ == "__main__":

    posts_url_before = import_data(folder="data_crowdtangle_url", file_name="posts_url_2020-06-02_.csv")
    posts_url_before = keep_only_one_year_data(posts_url_before)
    posts_url_before = clean_crowdtangle_url_data(posts_url_before)
    
    posts_url_after  = import_data(folder="data_crowdtangle_url", file_name="posts_url_2020-08-31_.csv")
    posts_url_after  = keep_only_one_year_data(posts_url_after)
    posts_url_after = clean_crowdtangle_url_data(posts_url_after)

    print_table_1(posts_url_before, posts_url_after)
    print_table_2(posts_url_before, posts_url_after)