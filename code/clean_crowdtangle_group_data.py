import sys
import os

import pandas as pd


def import_all_csvs(DATE):

    df_path = os.path.join('.', 'data', 'data_crowdtangle_group', 'posts_group_' + DATE + '.csv')
    df = pd.read_csv(df_path)
    
    return df


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


def export_clean_csv(clean_df, SUFFIX):

    csv_path = os.path.join('.', 'data', 'data_crowdtangle_group', 'posts_' + SUFFIX + '.csv')
    clean_df.to_csv(csv_path, index=False)
    print("The '{}' file has been printed in the '{}' folder".format(
        csv_path.split('/')[-1], csv_path.split('/')[-2])
    )


if __name__=="__main__":

    DATE = sys.argv[1]
    SUFFIX = sys.argv[2]

    df = import_all_csvs(DATE)
    clean_df = clean_columns(df)
    export_clean_csv(clean_df, SUFFIX)

