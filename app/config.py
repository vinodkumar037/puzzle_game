from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
try:
    client = MongoClient(uri)
    client.admin.command('ping')
    db = client(os.getenv("MONGODB_DB_NAME", "puzzle_game"))
    puzzle_game = client["puzzle_game"]
    print("Connected to MongoDB successfully!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

