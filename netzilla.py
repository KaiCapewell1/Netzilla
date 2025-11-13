from flask import Flask, render_template, request, url_for, redirect, jsonify
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

    # Call your Python function
    get_data.fetch_movie_data(movie_title, movie_year)

    # Return JSON to the frontend
    return jsonify({"status": "ok", "title": movie_title, "year": movie_year})

if __name__ == "__main__":
    app.run(debug=True)
