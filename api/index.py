import logging
import traceback
from flask import Flask, render_template, request, jsonify
import get_data

logging.basicConfig(level=logging.DEBUG)

# -------------------------------
# Create Flask app
# -------------------------------
app = Flask(__name__)

# -------------------------------
# Global error handler
# -------------------------------
@app.errorhandler(Exception)
def handle_exception(e):
    print("=========== SERVER ERROR ===========")
    traceback.print_exc()
    print("=========== END ERROR =============")
    return jsonify({"error": str(e)}), 500

# -------------------------------
# Routes
# -------------------------------
@app.route("/")
def get_posters():
    try:
        get_data.Load_images()
    except Exception as e:
        traceback.print_exc()
        return f"Error loading images: {e}", 500

    return render_template("index.html", posters=get_data.all_posters)


@app.route("/poster_click", methods=["POST"])
def poster_click():
    try:
        data = request.get_json()
        movie_title = data.get("title")
        movie_year = data.get("year")

        entertainment_type = None

        for era, posters in get_data.all_posters.items():
            for poster in posters:
                req_year = int(movie_year) if movie_year else None
                if poster[0] == movie_title and poster[1] == req_year:
                    entertainment_type = poster[3]
                    break
            if entertainment_type:
                break

        if entertainment_type is None:
            return jsonify({"error": f"NOT FOUND: {movie_title} ({movie_year})"}), 404

        result = get_data.fetch_movie_data(movie_title, movie_year, entertainment_type)
        return render_template("movie.html", movie=result)

    except Exception as e:
        traceback.print_exc()
        return f"ERROR IN poster_click: {e}", 500

# -------------------------------
# For local testing
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)
