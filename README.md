# WEBCLIM

[WebClim](https://medialab.sciencespo.fr/activites/webclim/) is a research project in Sciences Po's medialab. Our goal is to analyze the fake news ecosystem about climate change, and other scientific topics, on Facebook, Twitter, Youtube, and other platforms. This repo is about Facebook data collection and analysis.

## Set up

All the commands described in this README were run on Ubuntu 18.04.5.

This project was developed on Python 3.8.3, so you should first install Python. Then run these commands in your terminal (in a virtualenv if you prefer):

```
git clone https://github.com/medialab/webclim_facebook
cd webclim_facebook
pip install -r requirements.txt
```

To collect data from CrowdTangle, a CrowdTangle token is needed, and you should write it in a `.minetrc` file at the root similar to the `.minetrc.example` file.

## Collect the data

### Extract the Science Feedback dataset

You should export the following tables in a CSV format from the Science Feedback Airtable database, add the day's date in their name, and put them in the `sciencefeedback` folder:
* "Appearances-Grid view 2020-06-29.csv"
* "Reviews _ Fact-checks-Grid view 2020-06-29.csv"

### Collect the Facebook posts sharing these URLs

You should first clean the Science Feedback data, and then do the CrowdTangle request. Warning: the second command will take a few hours to run!
```
python code/clean_sciencefeedback_data.py 2020-08-27
./code/collect_crowdtangle_data_by_url.sh 2020-08-27
```

The commands can also be lauched for specific data, as only the ones related to climate, health or covid:
```
python code/clean_sciencefeedback_data.py 2020-06-29 covid
./code/collect_crowdtangle_data_by_url.sh 2020-06-29 covid
```

### Collect all the Facebook posts of a set of group

You should first have the list of the Facebook groups you want to collect. To see this list, you can write in a Jupyter Notebook:

```
import pandas as pd
pd.set_option('display.max_rows', None)

posts_df = pd.read_csv("./crowdtangle_url/posts_url_2020-06-29.csv")
posts_df = posts_df.drop_duplicates(subset=['url', 'account_url'])
posts_df["account_url"].value_counts()
```

You can now select the Facebook accounts sharing more than X fake news, and manually add the accounts you want to collect via their URLs on the Crowdtangle interface in a list (the list is different for groups and pages).

Then you will need the list ids to run the collect. All the list ids tied to a CrowdTangle account can be printed with:

```
minet ct lists
```

To collect the data you need to add the corresponding list id to the following command:

```
./code/collect_crowdtangle_data_by_group.sh <insert-list-id-here>
```

The output file's name will contain today's date. It can be cleaned and renamed with the following command:
```
python code/clean_crowdtangle_group_data.py 2020-09-01 fake_news_group
```

## Analyse the data

To reproduce the results in the methodological draft:
```
python code/methodo_paper.py
```

To reproduce the results in the draft in preparation for the IP&M special issue:

```
python code/ip&m_paper_part_2.py
python code/ip&m_paper_part_1.py
```

And for the first results for the QAnon draft:

```
python code/qanon_paper.py
```

The figures saved as PNG in the `figure` folder, and the content of the tables will be either printed in the console or saved as CSV in the same folder.

## Generate a draft

First you should install Latex with:

```
sudo apt-get install texlive-full
```

To generate the PDF used to submit to the Web Conference 2021, you should run:

```
cd article/
pdflatex webclim-facebook
bibtex webclim-facebook
pdflatex webclim-facebook
pdflatex webclim-facebook
```