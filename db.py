import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variables
mongo_uri = os.getenv("MONGO_URI")

# Create a connection to the MongoDB server
client = MongoClient(mongo_uri)

# Access your database
db = client.RealAwesome  # Replace with your database name

# Access collections (similar to tables in SQL)
users = db.users  # Example collection
courses = db.courses
materials = db.materials