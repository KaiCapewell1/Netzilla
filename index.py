from flask import Flask, render_template, request, jsonify
import get_data

app = Flask(__name__)  

@app.route("/")
def get_posters():
    get_data.Load_images()
    return render_template("index.html", posters=get_data.all_posters)

@app.route("/poster_click", methods=["POST"])
def poster_click():
    data = request.get_json()
    movie_title = data.get("title")
    movie_year = data.get("year")
    country_origin = data.get("country")

    entertainment_type = None
    for era, posters in get_data.all_posters.items():
        for poster in posters:
            try:
                req_year = int(movie_year) if movie_year else None
            except ValueError:
                req_year = None 

            if poster[0] == movie_title and poster[1] == req_year:
                entertainment_type = poster[3]
                if not country_origin and len(poster) > 4:
                    country_origin = poster[4]
                break
        if entertainment_type:
            break

    if not entertainment_type:
        return jsonify({"error": "Movie not found"}), 404
    
    result = get_data.fetch_movie_data(movie_title, movie_year, entertainment_type, country_origin)
    return render_template("movie.html", movie=result)

if __name__ == "__main__":
    app.run(debug=True)