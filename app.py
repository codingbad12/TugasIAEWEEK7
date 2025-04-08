from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
import requests
import json

app = Flask(__name__)
load_dotenv()

IMDB_API_KEY = os.getenv("API_KEY")
MOVIE_LIST_FILE = "watchlist.json"

def load_movies():
    if os.path.exists(MOVIE_LIST_FILE):
        with open(MOVIE_LIST_FILE, "r") as f:
            return json.load(f)
    return []

def save_movies(movies):
    with open(MOVIE_LIST_FILE, "w") as f:
        json.dump(movies, f, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/search")
def search():
    query = request.args.get("q")
    if not query:
        return jsonify([])

    url = f"http://www.omdbapi.com/?apikey=API_KEY&s={query}"
    try:
        res = requests.get(url)
        data = res.json()
        results = [
            {"id": item["imdbID"], "title": item["Title"], "image": item["Poster"]}
            for item in data.get("Search", [])[:5]
        ]
        return jsonify(results)
    except Exception as e:
        print("Error calling IMDb API:", e)
        return jsonify([])

@app.route("/list")
def list_movies():
    return jsonify(load_movies())

@app.route("/add", methods=["POST"])
def add_movie():
    movie = request.get_json()
    movie["status"] = "plan"
    movies = load_movies()
    if not any(m["id"] == movie["id"] for m in movies):
        movies.append(movie)
        save_movies(movies)
    return ("", 204)

@app.route("/update/<id>", methods=["PUT"])
def update_status(id):
    status = request.get_json().get("status")
    movies = load_movies()
    for movie in movies:
        if movie["id"] == id:
            movie["status"] = status
            break
    save_movies(movies)
    return ("", 204)

@app.route("/delete/<id>", methods=["DELETE"])
def delete_movie(id):
    movies = load_movies()
    movies = [m for m in movies if m["id"] != id]
    save_movies(movies)
    return ("", 204)

if __name__ == "__main__":
    app.run(port=8080)
