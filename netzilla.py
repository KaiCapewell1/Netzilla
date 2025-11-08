from flask import Flask, render_template, request, url_for, redirect
import get_data
import movies
app = Flask(__name__)  

@app.route("/")
def get_posters():
    get_data.Load_images()
    return render_template("index.html", posters=get_data.all_posters)

if __name__ == "__main__":
    app.run(debug=True)