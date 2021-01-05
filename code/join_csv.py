import pandas as pd 


df1 = pd.read_csv('./data/crowdtangle_url/posts_url_2021-01-03_.csv')
print(df1.url.nunique())

df2 = pd.read_csv('./data/crowdtangle_url/posts_url_2021-01-04_.csv', low_memory=False)
print(df2.url.nunique())

df = pd.concat([df1, df2])
print(df.url.nunique())

df.to_csv('./data/crowdtangle_url/posts_url_2021-01-04_test.csv')