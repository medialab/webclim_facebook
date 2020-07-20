import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np


posts_df = pd.read_csv("./data_crowdtangle_group/posts_group_2020-07-15_simple.csv")
posts_df['date'] = pd.to_datetime(posts_df['date'])
posts_df = posts_df[posts_df['date'] <= "2020-07-14"]

plt.figure(figsize=(12, 10))
plt.subplot(211)

plt.plot(posts_df.groupby(by=["date"])["reaction"].sum()/posts_df.account_id.nunique(), 
         label="Mean number of reactions per day")

plt.plot(posts_df.groupby(by=["date"])["comment"].sum()/posts_df.account_id.nunique(), 
         label="Mean number of comments per day")

plt.plot(posts_df.groupby(by=["date"])["share"].sum()/posts_df.account_id.nunique(), 
         label="Mean number of shares per day")

plt.title("The average daily popularity for the {} Facebook groups".format(posts_df.account_id.nunique()))
plt.legend()

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    
plt.xlim(np.datetime64('2019-08-26'), np.datetime64('2020-07-18'))
plt.ylim(bottom=0)


plt.subplot(212)

plt.plot(posts_df["date"].value_counts().sort_index()/posts_df.account_id.nunique(), 
    label="Mean number of posts per day", color="red")

plt.title("The average daily posts for the {} Facebook groups".format(posts_df.account_id.nunique()))
plt.legend()

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    
plt.xlim(np.datetime64('2019-08-26'), np.datetime64('2020-07-18'))
plt.ylim(bottom=0)
plt.show()