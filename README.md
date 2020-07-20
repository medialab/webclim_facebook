# WEBCLIM

[WebClim](https://medialab.sciencespo.fr/activites/webclim/) is a research project in Sciences Po's medialab. Our goal is to analyze the fake news ecosystem about climate change, and other scientific topics, on Facebook, Twitter, Youtube, and other platforms.

python src/clean_sciencefeedback_data.py

### Set up

This project was developed on Python 3.8.3, so you should first install Python. 
Then run these commands in your terminal (in a virtualenv if you prefer):

```
git clone https://github.com/medialab/webclim_facebook
cd webclim_facebook
pip install -r requirements.txt
```

### Extract the Science Feedback dataset

You should export the following tables in a CSV format from the Science Feedback Airtable database, add the day's date in their name, and put them in the `data_sciencefeedback` folder:
* "Appearances-Grid view 2020-06-29.csv"
* "Reviews _ Fact-checks-Grid view 2020-06-29.csv"

### Collect the Facebook posts sharing these URLs

You should get a CrowdTangle token and write it in a `config.json` file similar to the `config.json.example` file 
(except that you should write the token value instead of "blablabla").

You should first clean the Science Feedback data, and then do the CrowdTangle request. Warning: the second command will take a few hours to run!
```
python src/clean_sciencefeedback_data.py 
./src/collect_crowdtangle_data_by_url.sh
```

### Collect all the Facebook posts of the groups sharing these URLs

You should first have the list of the Facebook groups you want to collect. To see this list, you can write in a Jupyter Notebook:

```
import pandas as pd
pd.set_option('display.max_rows', None)

posts_df = pd.read_csv("./data_crowdtangle_url/posts_url_2020-06-29.csv")
posts_df["account_url"].value_counts()
```

We prefer to display the Facebook groups' URL because it is easier to search the groups using their URL on the CrowdTangle interface.

Then we need to manually add the groups you want to collect on the Crowdtangle interface and run this command:

```
./src/collect_crowdtangle_data_by_group.sh 1
```

Because collecting hundreds of groups takes days to run, we are manually adding a batch of a few groups each time and running the command whith increasing numbers in the argument. The output files will appear in the `data_crowdtangle_group` folder and will be named:
* posts_group_2020-07-15_1.csv
* posts_group_2020-07-15_2.csv
* posts_group_2020-07-15_3.csv
* ...

If you collect 6 different csv files you can then aggregate and clean your data with:
```
python ./src/aggregate_crowdtangle_group_data.py 6 2020-07-15
```

### Plot the temporal evolution

We can now plot the average popularity and number of posts for all the collected groups with the command:
```
python ./src/plot_mean_popularity.py
```
