from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
mongo_client = MongoClient(os.getenv("MONGO_URI"))
movie_finder_db = mongo_client["movie_finder"]

movies_collection = movie_finder_db["movies"]
favorites_collection = movie_finder_db["favorites"]
