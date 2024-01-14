import os
import requests

def scrape_hashtag(hashtag):
    hashtag_uid = None

    url = "https://tokapi-mobile-version.p.rapidapi.com/v1/search/hashtag"

    querystring = {
        "keyword": hashtag,
        "count": "1"
    }

    headers = {
        "X-RapidAPI-Key": os.getenv('RAPIDAPI_KEY'),
        "X-RapidAPI-Host": "tokapi-mobile-version.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    if data.get('challenge_list') and len(data['challenge_list']) > 0:
        challenge_info = data['challenge_list'][0]['challenge_info']
        hashtag_uid = challenge_info.get('cid')

    return hashtag_uid
