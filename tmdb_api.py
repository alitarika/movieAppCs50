import requests

TMDB_API_KEY = "eef7b2622bdba952fd2f2f4fa88395b6"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
# TMDB_POSTER_URL = "https://image.tmdb.org/t/p/original"

def fetch_movie_by_query(movie_title):
    # Construct the API URL
    url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": movie_title,
    }

    # Send a GET request to the TMDb API
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get('results'):
            # Return data for the first movie found
            return data['results']
        else:
            return []
    
    return None


def fetch_movie_by_id(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    
    return None


def fetch_actor_by_id(movie_id):
    # Construct the API URL
    url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits?language=en-US"
    params = {
        "api_key": TMDB_API_KEY
    }

    # Send a GET request to the TMDb API
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get('cast'):
            # Return data for the first movie found
            return data['cast']
        else:
            return []
    
    return [] # return None


def fetch_director_by_id(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits?language=en-US"
    params = {
        "api_key": TMDB_API_KEY
    }

    # Send a GET request to the TMDb API
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        directors = []
        if data.get('crew'):
            for person in data["crew"]:
                if person["job"] == "Director":
                    directors.append(person)
        return directors
    else:
        return None

def fetch_writer_by_id(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}/credits?language=en-US"
    params = {
        "api_key": TMDB_API_KEY
    }

    # Send a GET request to the TMDb API
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        writers = []
        if data.get('crew'):
            for person in data["crew"]:
                if person["job"] == "Writer":
                    writers.append(person)
        return writers
    else:
        return None
    

def fetch_person_details(person_id):
    url = f"{TMDB_BASE_URL}/person/{person_id}?language=en-US"
    params = {
        "api_key": TMDB_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    
    return None


def fetch_person_movie_credits(person_id):
    url = f"{TMDB_BASE_URL}/person/{person_id}/movie_credits?language=en-US"
    params = {
        "api_key": TMDB_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    
    return None

def fetch_poster_and_title_by_id(movie_id):
    # Get movie data using fetch_movie_by_id
    movie_data = fetch_movie_by_id(movie_id)

    if movie_data:
        # Extract the "poster_path" and "title" from the movie data
        poster_path = movie_data.get("poster_path", "")
        title = movie_data.get("title", "")

        return {
            "poster_path": poster_path,
            "title": title
        }
    else:
        return None