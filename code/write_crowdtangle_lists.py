import pandas as pd

from utils import (import_data, export_data)


pd.options.display.max_colwidth = 300

def create_template_csv_from_serie(serie, list_name):

    df = pd.DataFrame(columns=["Page or Account URL", "List"])
    df["Page or Account URL"] = serie.index
    df["List"] = list_name

    export_data(df, 'crowdtangle_list', list_name + '.csv')

    return df


if __name__=="__main__":

    df = import_data(folder="crowdtangle_url", file_name="posts_url_2021-01-04_.csv")    
    df = df.drop_duplicates(subset=['url', 'account_id'])
    s = df["account_url"].value_counts()

    top1_df = create_template_csv_from_serie(s[s > 45], "heloise_fake_news_groups_1")
    top2_df = create_template_csv_from_serie(s[(s <= 45) & (s > 35)], "heloise_fake_news_groups_2")
    top3_df = create_template_csv_from_serie(s[(s <= 35) & (s > 29)], "heloise_fake_news_groups_3")
    top4_df = create_template_csv_from_serie(s[(s <= 29) & (s > 26)], "heloise_fake_news_groups_4")
    top5_df = create_template_csv_from_serie(s[(s <= 26) & (s > 23)], "heloise_fake_news_groups_5")

    print(len(top1_df))
    print(len(top2_df))
    print(len(top3_df))
    print(len(top4_df))
    print(len(top5_df))

    top6_df = create_template_csv_from_serie(s[s > 23], "heloise_fake_news_pages")
    print(len(top6_df))