import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

# Load environment variables
load_dotenv()


mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    print("Error: MONGO_URI not found in environment variables")
    sys.exit(1)

try:
    # Create a connection to the MongoDB server
    client = MongoClient(mongo_uri)
    
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
    

    db = client.RealAwesome
    
    # Access collections
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
