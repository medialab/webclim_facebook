import os
import datetime

import pandas as pd
import numpy as np

from ipm_paper_part_1 import concatenate_crowdtangle_group_data
from utils import import_data


### LIST ACCOUNTS PART 1

df_list = []
for set_date in ['2021-01-05', '2021-01-06', '2021-01-07', '2021-01-08', '2021-01-09', '2021-01-10']:
#for set_date in ['2021-01-05']:
    temp_df = import_data(folder="crowdtangle_group", file_name="posts_group_" + set_date + ".csv")
    temp_df = temp_df.drop_duplicates(subset=['account_name'])
    df_list.append(temp_df)
    print(len(temp_df))

base_df = pd.concat(df_list)
base_df = base_df[['account_id', 'account_url', 'account_name', 'account_subscriber_count']]
base_df['account_id'] = base_df['account_id'].astype(int)


base_df['june_drop'] = np.nan

posts_fake = concatenate_crowdtangle_group_data("fake_news_2021")
posts_fake['total_engagement'] = posts_fake['reaction'] + posts_fake['share'] + posts_fake['comment']
posts_fake = posts_fake[
    (posts_fake['date'] >= datetime.datetime.strptime('2020-06-08', '%Y-%m-%d')) &
    (posts_fake['date'] <= datetime.datetime.strptime('2020-06-10', '%Y-%m-%d'))
]

for account_id in posts_fake.account_id.unique():
    posts_temp = posts_fake[posts_fake['account_id'] == account_id]
    before = posts_temp[posts_temp['date'] == '2020-06-08']['total_engagement'].values
    after = posts_temp[posts_temp['date'] == '2020-06-10']['total_engagement'].values
    if (len(posts_temp[posts_temp['date'] == '2020-06-08']) > 0 and 
        len(posts_temp[posts_temp['date'] == '2020-06-10']) > 0 and
        np.mean(before) > 0):
        june_drop = str(int(np.round((np.mean(after) - np.mean(before)) * 100 / np.mean(before), 0))) + '%'
        base_df.loc[base_df['account_id']==account_id, ['june_drop']] = [june_drop]


df = import_data(folder="crowdtangle_url", file_name="posts_url_2021-01-04_.csv") 
df = df.drop_duplicates(subset=['url', 'account_id'])
df = df.dropna(subset=['url', 'account_id'])
df['account_id'] = df['account_id'].astype(int)
s = df["account_id"].value_counts()
s = s[s > 23].to_frame()
s = s.rename(columns={'account_id': 'strike_number'})
s['account_id'] = s.index

base_df = base_df.merge(s, how='left', on='account_id')
base_df = base_df.drop(columns=['account_id'])


supplementary_table_path = os.path.join(".", "data", "crowdtangle_list", "account_list_part_1.csv")
base_df.to_csv(supplementary_table_path, index=False)


### LIST ACCOUNTS PART 2

# posts_1 = import_data(folder="crowdtangle_group", file_name="posts_group_2021-01-05.csv")
# posts_1 = posts_1.drop_duplicates(subset=['account_name'])
# print(len(posts_1))

# posts_2 = import_data(folder="crowdtangle_group", file_name="posts_group_2021-01-06.csv")
# posts_2 = posts_2.drop_duplicates(subset=['account_name'])
# print(len(posts_2))

# posts = pd.concat([posts_1, posts_2])
# posts = posts[['account_id', 'account_url', 'account_name', 'account_subscriber_count']]
# print(posts)


# pages_df = import_data(folder="crowdtangle_list", file_name="self_declared_page_details.csv")
# supplementary_table = pages_df[['post_url', 'date', 'page_name', 'page_url']]

# posts_1 = import_data(folder="crowdtangle_group", file_name="posts_group_2021-01-11.csv")
# posts_2 = import_data(folder="crowdtangle_group", file_name="posts_group_2021-01-12.csv")
# posts_df = pd.concat([posts_1, posts_2])

# posts_df = posts_df.drop_duplicates(subset=['account_name'])
# posts_df = posts_df[['account_name', 'account_subscriber_count']]

# supplementary_table = supplementary_table.merge(posts_df, how='left', 
#                                                 left_on='page_name', right_on='account_name')
# supplementary_table = supplementary_table.drop(columns=['account_name'])
# supplementary_table = supplementary_table.rename(columns={'account_subscriber_count': 'page_subscriber_number'})

# supplementary_table_path = os.path.join(".", "data", "crowdtangle_list", "page_list_part_2.csv")
# supplementary_table.to_csv(supplementary_table_path, index=False)