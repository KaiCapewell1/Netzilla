from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import os
from movies import era_movies

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
IMAGE_URL = os.getenv("IMAGE_URL")

all_posters = [] 


def search_api(type, movie_name, movie_year):
    params = {"query": movie_name, "language": "en-US", "api_key": API_KEY, "year": movie_year}
    response = requests.get(f"{BASE_URL}/search/{type}", params=params)
    response.raise_for_status()
    return response.json().get("results", [])


def fetch_poster(movie):
    movie_name = movie[0] if isinstance(movie, tuple) else movie
    movie_year = movie[1] if isinstance(movie, tuple) else None
    try:
        results = search_api("movie", movie_name, movie_year)
        if not results:
            results = search_api("tv", movie_name, movie_year)
        if not results:
            print(f"No results found for {movie_name} ({movie_year})")
            return (movie_name, None)
        
        poster_path = results[0].get("poster_path")
        if poster_path:
          return (movie_name, movie_year, f"{IMAGE_URL}{poster_path}")
    except Exception as e:
        print(f"Error fetching poster for {movie_name} ({movie_year}): {e}")
    return (movie_name, movie_year, None)


def Load_images():
    global all_posters
    all_posters = {era: [] for era in era_movies}

    with ThreadPoolExecutor(max_workers=10) as executor: # using threading for faster API calls making the website loads faster 
        futures = []
        for era, movies_list in era_movies.items():
            for movie in movies_list:
                futures.append((era, executor.submit(fetch_poster, movie)))

        for era, fut in futures:
            movie_name, movie_year, poster_url = fut.result()
            if poster_url:
                print(f"Adding poster for {movie_name}, {movie_year}, {poster_url}")
                all_posters[era].append((movie_name, movie_year, poster_url))
            else:
                print(f"Poster not found for {movie_name}")
    sort_posters(all_posters)

def sort_posters(all_posters):
    for era, posters in all_posters.items():
        posters.sort(key=lambda x: (x[1] if x[1] is not None else 0, x[0])) # Sort by year, then by name
    return all_posters


def fetch_movie_data(movie_title, movie_year):
    print(f"succsess {movie_title}, {movie_year}")



if __name__ == "__main__":
    Load_images()
