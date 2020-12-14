import os
from datetime import datetime

from dotenv import load_dotenv
import requests


load_dotenv()
BUZZSUMO_API_KEY = os.getenv('BUZZSUMO_API_KEY')

domain_name_example = 'lemonde.fr'

params = {
    'q': domain_name_example,
    'api_key': BUZZSUMO_API_KEY,
    'num_results': 100,
    'begin_date': datetime.timestamp(datetime.strptime('2020-06-07', '%Y-%m-%d')),
    'end_date': datetime.timestamp(datetime.strptime('2020-06-11', '%Y-%m-%d'))
}
r = requests.get('https://api.buzzsumo.com/search/articles.json', params=params)
data = r.json()

for i in range(len(data['results'])):
    print(
        # data['results'][1]['domain_name'],
        data['results'][i]['url'], 
        # datetime.fromtimestamp(data['results'][i]['published_date'])
        data['results'][i]['total_shares'],
        data['results'][i]['total_reddit_engagements'], 
        data['results'][i]['twitter_shares'],
        data['results'][i]['total_facebook_shares'],
        # data['results'][1]['facebook_shares'],
        # data['results'][1]['facebook_likes'],
        # data['results'][1]['facebook_comments'],
    )

total_pages = data['total_pages']
print(data['total_results'])

# r = requests.get(
#     'https://api.buzzsumo.com/search/articles.json', 
#     params={**params, 'page': total_pages - 1}
# )
# data = r.json()

# print(
#     # data['results'][-1]['domain_name'],
#     # data['results'][-1]['url'], 
#     datetime.fromtimestamp(data['results'][-1]['published_date'])
# )
