import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Load environment variables
load_dotenv()

# Get MongoDB connection string from environment variables
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    print("Error: MONGO_URI not found in environment variables")
    sys.exit(1)

try:
    # Create a connection to the MongoDB server
    client = MongoClient(mongo_uri)
    
    # Verify the connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    
    # Access your database
    db = client.RealAwesome
    
    # Access collections (similar to tables in SQL)
    users = db.users
    courses = db.courses
    materials = db.materials
    discussions = db.discussions

except ConnectionFailure as e:
    print(f"Could not connect to MongoDB: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}")
    sys.exit(1)