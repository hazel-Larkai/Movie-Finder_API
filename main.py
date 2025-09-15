from fastapi import FastAPI, HTTPException, Form
from pydantic import BaseModel
from bson import ObjectId
import requests, os
from dotenv import load_dotenv
from db import movies_collection, favorites_collection
from utils import replace_mongo_id
from typing import Annotated

app = FastAPI()

class FavoriteMovie(BaseModel):
    title: str
    year: str
    genre: str
    imdbID: str
    user_rating: float


# Get Homepage
@app.get("/")
def home():
    return {"message": "Welcome to Movie Finder"}


@app.get("/movies")
def get_movie(title: str):
    url = f"http://www.omdbapi.com/?t={title}&apikey=49803d3d"

    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Error contacting OMDb API")

    data = response.json()
    if "Response" not in data:
        raise HTTPException(status_code=404, detail="Movie not found")

    movie_info = {
        "title": data["Title"],
        "year": data["Year"],
        "genre": data["Genre"],
        "imdbID": data["imdbID"],
    }

    existing = movies_collection.find_one({"imdbID": movie_info["imdbID"]})
    if not existing:
        result = movies_collection.insert_one(movie_info)
        movie_info["_id"] = str(result.inserted_id)
    else:
        movie_info = replace_mongo_id(existing)

    return movie_info


@app.post("/favorites")
def add_favorite(
    title: Annotated[str, Form()],
    year: Annotated[str, Form()],
    genre: Annotated[str, Form()],
    imdbID: Annotated[str, Form()],
    user_rating: Annotated[float, Form()],
):
    existing = favorites_collection.find_one({"imdbID": imdbID})
    if existing:
        raise HTTPException(status_code=409, detail="Movie already in favorites")

    # Insert into MongoDB
    result = favorites_collection.insert_one(
        {
            "title": title,
            "year": year,
            "genre": genre,
            "imdbID": imdbID,
            "user_rating": user_rating,
        }
    )

    return {"message": f"{title} saved to favorites!", "id": str(result.inserted_id)}


# List all favorites
@app.get("/favorites")
def list_favorites():
    favorites = [replace_mongo_id(movie) for movie in favorites_collection.find()]
    return favorites
