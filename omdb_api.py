import requests

OMDB_API_KEY = "b5af876a"

def omdb_by_imdb_id(imdb_id):
    params = {
        'i': imdb_id,
        'apikey': OMDB_API_KEY
    }

    omdb_url = 'http://www.omdbapi.com/'

    response = requests.get(omdb_url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        return None
