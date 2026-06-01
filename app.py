import os

import requests
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, send_from_directory, url_for

from data_manager import DataManager
from models import db, Movie, User

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'data/movies.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

db.init_app(app)

data_manager = DataManager()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")


def fetch_movie_from_omdb(title):
    if not OMDB_API_KEY:
        return None
    try:
        resp = requests.get(
            "http://www.omdbapi.com/",
            params={"t": title, "apikey": OMDB_API_KEY},
            timeout=5,
        )
        data = resp.json()
        if data.get("Response") == "True":
            year = data.get("Year", "")
            try:
                year = int(year[:4])
            except (ValueError, TypeError):
                year = None
            return {
                "director": data.get("Director", ""),
                "year": year,
                "poster_url": data.get("Poster", ""),
            }
    except requests.RequestException:
        pass
    return None


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500


@app.route("/")
def index():
    users = data_manager.get_users()
    return render_template("index.html", users=users)


@app.route("/users", methods=["POST"])
def create_user():
    name = request.form["name"]
    data_manager.create_user(name)
    return redirect(url_for("index"))


@app.route("/users/<int:user_id>/edit")
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template("edit_user.html", user=user)


@app.route("/users/<int:user_id>/update", methods=["POST"])
def update_user(user_id):
    new_name = request.form.get("name")
    if new_name:
        data_manager.update_user(user_id, new_name)
    return redirect(url_for("index"))


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    data_manager.delete_user(user_id)
    return redirect(url_for("index"))


@app.route("/users/<int:user_id>/movies", methods=["GET", "POST"])
def get_movies(user_id):
    if request.method == "POST":
        title = request.form["name"]
        info = fetch_movie_from_omdb(title)
        if info:
            movie = Movie(
                name=title,
                director=info["director"],
                year=info["year"],
                poster_url=info["poster_url"],
                user_id=user_id,
            )
        else:
            movie = Movie(name=title, user_id=user_id)
        data_manager.add_movie(movie)
        return redirect(url_for("get_movies", user_id=user_id))

    user = User.query.get(user_id)
    if not user:
        return render_template("404.html"), 404
    movies = data_manager.get_movies(user_id)
    return render_template("movies.html", movies=movies, user=user)


@app.route("/users/<int:user_id>/movies/<int:movie_id>/update", methods=["POST"])
def update_movie(user_id, movie_id):
    new_title = request.form.get("name")
    if new_title:
        data_manager.update_movie(movie_id, new_title)
    return redirect(url_for("get_movies", user_id=user_id))


@app.route("/users/<int:user_id>/movies/<int:movie_id>/delete", methods=["POST"])
def delete_movie(user_id, movie_id):
    data_manager.delete_movie(movie_id)
    return redirect(url_for("get_movies", user_id=user_id))


@app.route("/docs")
def docs():
    return send_from_directory(basedir, "docs.html")


@app.route("/openapi.yaml")
def openapi_spec():
    return send_from_directory(basedir, "openapi.yaml")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)
