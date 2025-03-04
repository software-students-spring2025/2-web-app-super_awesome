import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")

client = MongoClient(mongo_uri)
db = client.RealAwesome

users = db.users
courses = db.courses
materials = db.materials
discussions = db.discussions
