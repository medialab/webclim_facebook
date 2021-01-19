import os

import pandas as pd

from utils import import_data


pages_df = import_data(folder="crowdtangle_list", file_name="self_declared_page_details.csv")
supplementary_table = pages_df[['post_url', 'date', 'page_name', 'page_url']]

posts_1 = import_data(folder="crowdtangle_group", file_name="posts_group_2021-01-11.csv")
posts_2 = import_data(folder="crowdtangle_group", file_name="posts_group_2021-01-12.csv")
posts_df = pd.concat([posts_1, posts_2])

posts_df = posts_df.drop_duplicates(subset=['account_name'])
posts_df = posts_df[['account_name', 'account_subscriber_count']]

supplementary_table = supplementary_table.merge(posts_df, how='left', 
                                                left_on='page_name', right_on='account_name')
supplementary_table = supplementary_table.drop(columns=['account_name'])
supplementary_table = supplementary_table.rename(columns={'account_subscriber_count': 'page_subscriber_number'})

supplementary_table_path = os.path.join(".", "data", "crowdtangle_list", "page_list_part_2.csv")
supplementary_table.to_csv(supplementary_table_path, index=False)