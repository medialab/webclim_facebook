import os
from datetime import datetime

from dotenv import load_dotenv
import requests


load_dotenv()
BUZZSUMO_API_KEY = os.getenv('BUZZSUMO_API_KEY')

domain_name_example = 'lemonde.fr'

params = {
    'q': domain_name_example,
    'api_key': BUZZSUMO_API_KEY
}
r = requests.get('https://api.buzzsumo.com/search/articles.json', params=params)
data = r.json()

total_pages = data['total_pages']

print(
    data['results'][1]['domain_name'],
    data['results'][1]['url'], 
    datetime.fromtimestamp(data['results'][1]['published_date'])
    # data['results'][1]['total_reddit_engagements'], 
    # data['results'][1]['twitter_shares'],
    # data['results'][1]['facebook_shares'],
    # data['results'][1]['facebook_likes'],
    # data['results'][1]['facebook_comments'],
)

r = requests.get(
    'https://api.buzzsumo.com/search/articles.json', 
    params={**params, 'page': total_pages - 1}
)
data = r.json()

print(
    data['results'][-1]['domain_name'],
    data['results'][-1]['url'], 
    datetime.fromtimestamp(data['results'][-1]['published_date'])
)
