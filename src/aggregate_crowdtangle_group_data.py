import sys
import pandas as pd


def import_all_csvs(DATE, END):

    dfs = list()
    for csv_index in range(1, END + 1):
        print("Importing file number {}...".format(csv_index))
        dfs.append(pd.read_csv(
            "./data_crowdtangle_group/posts_group_{}_{}.csv".format(DATE, csv_index)
        ))
    
    return pd.concat(dfs)


def clean_columns(df):

    simple_df = pd.DataFrame(columns=[
        "account_name", "account_id",
        "date", "share", "comment", "reaction"
    ])

    simple_df['account_name'] = df['account_name'].astype(str)
    simple_df['account_id'] = df['account_id'].astype(int)

    simple_df['date'] = pd.to_datetime(df['date'])

    simple_df['account_id'] = df['account_id'].astype(int)
    simple_df["share"]   = df[["actual_share_count"]].astype(int)
    simple_df["comment"] = df[["actual_comment_count"]].astype(int)

    simple_df["reaction"] = df[["actual_like_count", "actual_favorite_count", "actual_love_count",
    "actual_wow_count", "actual_haha_count", "actual_sad_count",
    "actual_angry_count", "actual_thankful_count"]].sum(axis=1).astype(int)

    return simple_df


def export_clean_csv(simple_df):

    csv_path = "./data_crowdtangle_group/posts_group_{}_simple.csv".format(DATE)
    simple_df.to_csv(csv_path, index=False)
    print("The '{}' file has been printed in the '{}' folder".format(
        csv_path.split('/')[-1], csv_path.split('/')[-2])
    )


if __name__=="__main__":

    END = int(sys.argv[1])

    if len(sys.argv) >= 3:
        DATE = sys.argv[2]
    else:
        DATE = "2020-07-15"
        print("The date '{}' has been chosen by default.".format(DATE))

    df = import_all_csvs(DATE, END)
    simple_df = clean_columns(df)
    export_clean_csv(simple_df)





