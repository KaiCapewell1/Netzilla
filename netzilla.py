from flask import Flask, render_template, request, jsonify
import get_data
import os

app = Flask(__name__)

# -----------------------
# Routes
# -----------------------
@app.route("/")
def get_posters():
    try:
        get_data.Load_images()
    except Exception as e:
        return f"Error loading images: {e}", 500

    return render_template("index.html", posters=get_data.all_posters)


@app.route("/poster_click", methods=["POST"])
def poster_click():
    data = request.get_json()
    movie_title = data.get("title")
    movie_year = data.get("year")

    entertainment_type = None
    for era, posters in get_data.all_posters.items():
        for poster in posters:
            try:
                req_year = int(movie_year) if movie_year else None
            except ValueError:
                req_year = None

            if poster[0] == movie_title and poster[1] == req_year:
                entertainment_type = poster[3]
                break
        if entertainment_type:
            break

    if not entertainment_type:
        return jsonify({"error": f"Movie not found with title: {movie_title} and year: {movie_year}"}), 404

    try:
        result = get_data.fetch_movie_data(movie_title, movie_year, entertainment_type)
    except Exception as e:
        return f"Error fetching movie data: {e}", 500

    return render_template("movie.html", movie=result)


# -----------------------
# Main entry
# -----------------------
if __name__ == "__main__":
    ENV = os.environ.get("ENV", "development")
    port = int(os.environ.get("PORT", 5000))

    # Only run Flask's dev server in development
    if ENV != "production":
        app.run(host="0.0.0.0", port=port, debug=True)
