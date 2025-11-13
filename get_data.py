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
    results = search_api("movie", movie_name, movie_year)
    if results:
        poster_path = results[0].get("poster_path")
        if poster_path:
            return (movie_name, movie_year, f"{IMAGE_URL}{poster_path}", "movie")
            
    results = search_api("tv", movie_name, movie_year)
    if results:
        poster_path = results[0].get("poster_path")
        if poster_path:
            return (movie_name, movie_year, f"{IMAGE_URL}{poster_path}", "tv")
        
        return(movie_name, movie_year, None, None)
    

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
            movie_name, movie_year, poster_url, entertainment_type = fut.result()
            all_posters[era].append((movie_name, movie_year, poster_url, entertainment_type))
    sort_posters(all_posters)

def sort_posters(all_posters):
    for era, posters in all_posters.items():
        posters.sort(key=lambda x: (x[1] if x[1] is not None else 0, x[0])) # Sort by year, then by name
    return all_posters


def fetch_movie_data(movie_title, movie_year, entetainment_type):
    params = {"query": movie_title, "language": "en-US", "api_key": API_KEY, "year": movie_year}
    response = requests.get(f"{BASE_URL}/search/{entetainment_type}", params=params)
    results = response.json().get("results", [])

    if not results:
        return None
    
    result = results[0]

    details_response = requests.get(f"{BASE_URL}/{entetainment_type}/{result['id']}", params={"api_key": API_KEY, "language": "en-US"})
    details = details_response.json()


    movie_data = {
        "title": result.get("title") or result.get("name"),
        "year": movie_year,
        "overview": details.get("overview", ""),
        "ratings": round(details.get("vote_average", 0),1),
        "genres": [g["name"] for g in details.get("genres", [])],
        "poster_path": f"{IMAGE_URL}{details.get('poster_path', '')}",
        "director": None,
        "screenplay": None,
        "story": None,
        "trailer": None
    }

    

    if entetainment_type == "movie":
        credits_response = requests.get(f"{BASE_URL}/movie/{details['id']}/credits", params={"api_key": API_KEY})
        credits = credits_response.json()
        for crew_member in credits.get("crew", []):
            if crew_member["job"] == "Director":
                movie_data["director"] = crew_member["name"]
            elif crew_member["job"] == "Screenplay":
                movie_data["screenplay"] = crew_member["name"]
            elif crew_member["job"] == "Story":
                movie_data["story"] = crew_member["name"]

    movie_data["trailer"] = get_yt_trailer_link(movie_title, movie_year)

    if entetainment_type == "tv":
        creators = result.get("created_by", [])
        movie_data["creator"] = [c.get("name") for c in creators] if creators else None

    return movie_data

def get_yt_trailer_link(movie_title, movie_year):
    query = f"{movie_title} {movie_year} TOHO channel japanese trailer"
    youtube_search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        "part": "snippet",
        "q": query,
        "key": os.getenv("YOUTUBE_API_KEY"),
        "maxResults": 1,
        "type": "video"
    }
    response = requests.get(youtube_search_url, params=params)
    response.raise_for_status()
    results = response.json().get("items", [])
    if results:
        video_id = results[0]["id"]["videoId"]
        trailer = f"https://www.youtube.com/watch?v={video_id}"
        return trailer
    return None


if __name__ == "__main__":
    Load_images()

    
