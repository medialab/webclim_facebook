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

### Collect the Facebook groups sharing these URLs

You should get a CrowdTangle token and write it in a `config.json` file similar to the `config.json.example` file 
(except that you should write the token value instead of "blablabla").

You should first clean the Science Feedback data, and then do the CrowdTangle request. Warning: the second command will take a few hours to run!
```
python src/clean_sciencefeedback_data.py 
./src/collect_crowdtangle_data_by_url.sh
```
