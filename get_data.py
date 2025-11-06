from dotenv import load_dotenv
import requests
import os
from movies import era_movies

load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("BASE_URL")
IMAGE_URL = os.getenv("IMAGE_URL")

def search_api(type, movie_name, movie_year):
    params = {"query": movie_name, "language": "en-US", "api_key": API_KEY,"year": movie_year}
    response = requests.get(f"{BASE_URL}/search/{type}", params=params)
    response.raise_for_status()
    return response.json().get("results", [])

def Load_images(retries=3, timeout=10):
    for era, movies_list in era_movies.items():
        print(f"\n--- Era: {era} ---")
        for movie in movies_list:
            movie_name = movie[0] if isinstance(movie, tuple) else movie
            movie_year = movie[1] if isinstance(movie, tuple) else None

            attempts = retries

            while attempts > 0:
                try:
                   results = search_api("movie", movie_name, movie_year) # Search for movies first

                   if not results: # If no movie results, change type to TV shows and search again
                        print(f"No movie results found for {movie_name}, trying TV shows...")
                        results = search_api("tv", movie_name, movie_year)
                   if not results: # if still no results, break the loop
                        print(f"No TV show results found for {movie_name} either.")
                        break

                        
                   result = results[0]
                   poster_path = result.get("poster_path")
                   if poster_path:
                        poster_url = f"{IMAGE_URL}{poster_path}"
                        print(f"Poster URL for {movie_name}-{movie_year}: {poster_url}")
                   else:
                        
                        print(f"There are no poster(s) available for {movie_name}")
                   break


                except Exception as e:
                    print(f"Error fetching data for {movie_name}: {e}")
                    retries -= 1
                

if __name__ == "__main__":
    Load_images()

