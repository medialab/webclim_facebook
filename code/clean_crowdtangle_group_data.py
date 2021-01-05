import sys
import os

import pandas as pd

from utils import (import_data, export_data)


def clean_columns(df):

    clean_df = pd.DataFrame(columns=[
        "account_name", "account_id",
        "date", "share", "comment", "reaction"
    ])

    clean_df['account_name'] = df['account_name'].astype(str)
    clean_df['account_id'] = df['account_id'].astype(int)

    clean_df['date'] = pd.to_datetime(df['date'])

    clean_df['account_id'] = df['account_id'].astype(int)
    clean_df["share"]   = df[["actual_share_count"]].astype(int)
    clean_df["comment"] = df[["actual_comment_count"]].astype(int)

    clean_df["reaction"] = df[["actual_like_count", "actual_favorite_count", "actual_love_count",
    "actual_wow_count", "actual_haha_count", "actual_sad_count",
    "actual_angry_count", "actual_thankful_count"]].sum(axis=1).astype(int)

    return clean_df


if __name__=="__main__":

    DATE = sys.argv[1]
    SUFFIX = sys.argv[2]

    df = import_data(folder="crowdtangle_group", file_name='posts_group_' + DATE + '.csv')
    clean_df = clean_columns(df)
    export_data(clean_df, 'crowdtangle_group', 'posts_' + SUFFIX + '.csv')
