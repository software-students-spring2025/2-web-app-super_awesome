import os
import datetime
from bson.objectid import ObjectId
from gridfs import GridFS
from .db import users, courses, materials, discussions, db
from werkzeug.security import generate_password_hash

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.RealAwesome 

fs = GridFS(db)

def delete_gridfs_file(file_id_str):
    """Delete a file from GridFS."""
    try:
        if file_id_str.startswith('gridfs://'):
            file_id_str = file_id_str.replace('gridfs://', '')
        
        file_id = ObjectId(file_id_str)

        if fs.exists(file_id):
            fs.delete(file_id)
            return True
        return False
    except Exception as e:
        print(f"Error deleting GridFS file: {e}")
        return False
    
def create_user(username, email, password):
    """Create a new user in the database."""
    user = {
        "username": username,
        "name": username,  # Add name field to match app.py
        "email": email,
        "password": generate_password_hash(password),
        "date_joined": datetime.datetime.utcnow(),
        "uploads": [],
        "bookmarks": [],
        "discussions": [] 
    }
    result = users.insert_one(user)
    return result.inserted_id

def get_user_by_username(username):
    """Retrieve a user by username."""
    return users.find_one({"username": username})

def get_user_by_email(email):
    """Retrieve a user by email."""
    return users.find_one({"email": email})

def get_user_by_id(user_id):
    """Retrieve a user by ID."""
    return users.find_one({"_id": ObjectId(user_id)})

def update_user(user_id, update_data):
    """Update user information."""
    return users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )

def delete_user(user_id):
    """Delete a user from the database."""
    return users.delete_one({"_id": ObjectId(user_id)})

def add_bookmark(user_id, material_id):
    """Add a bookmark to a user's bookmarks list."""
    return users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"bookmarks": ObjectId(material_id)}}
    )

def remove_bookmark(user_id, material_id):
    """Remove a bookmark from a user's bookmarks list."""
    return users.update_one(
        {"_id": ObjectId(user_id)},
        {"$pull": {"bookmarks": ObjectId(material_id)}}
    )

# Course-related database operations
def create_course(course_code, title, department=None, description=None, instructor=None):
    """Create a new course in the database.
    
    Args:
        course_code (str): The course code (e.g., CS101)
        title (str): The course name/title
        department (str, optional): The department offering the course
        description (str, optional): Course description
        instructor (str, optional): Course instructor name
    
    Returns:
        ObjectId: The ID of the created course
    """
    course = {
        "code": course_code,
        "name": title,
        "department": department,
        "description": description,
        "instructor": instructor,
        "date_added": datetime.datetime.utcnow(),
        "materials_count": 0
    }
    result = courses.insert_one(course)
    return result.inserted_id

def get_all_courses():
    """Retrieve all courses from the database."""
    return list(courses.find())

def get_course_by_id(course_id):
    """Retrieve a course by ID."""
    return courses.find_one({"_id": ObjectId(course_id)})

def get_course_by_code(course_code):
    """Retrieve a course by course code."""
    return courses.find_one({"course_code": course_code})

def search_courses(query):
    """Search for courses by keyword."""
    return list(courses.find({
        "$or": [
            {"course_code": {"$regex": query, "$options": "i"}},
            {"title": {"$regex": query, "$options": "i"}},
            {"department": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}}
        ]
    }))

def update_course(course_id, update_data):
    """Update course information."""
    return courses.update_one(
        {"_id": ObjectId(course_id)},
        {"$set": update_data}
    )

def increment_materials_count(course_id):
    """Increment the materials count for a course."""
    return courses.update_one(
        {"_id": ObjectId(course_id)},
        {"$inc": {"materials_count": 1}}
    )

def decrement_materials_count(course_id):
    """Decrement the materials count for a course."""
    return courses.update_one(
        {"_id": ObjectId(course_id)},
        {"$inc": {"materials_count": -1}}
    )

def delete_course(course_id):
    """Delete a course from the database."""
    return courses.delete_one({"_id": ObjectId(course_id)})

# Material-related database operations
def create_material(title, description, course_id, uploader_id, file_path, material_type):
    """Create a new material entry in the database."""
    storage_type = get_storage_type(file_path)
    material = {
        "name": title,  
        "title": title,
        "description": description,
        "course_id": ObjectId(course_id),
        "uploader_id": ObjectId(uploader_id),
        "file_path": file_path,
        "storage_type":storage_type,
        "material_type": material_type,
        "upload_date": datetime.datetime.utcnow(),
        "ratings": [],
        "avg_rating": 0,
        "downloads": 0,
        "comments": []
    }
    result = materials.insert_one(material)
    
    # Update course materials count
    increment_materials_count(course_id)
    
    # Add to user's uploads
    users.update_one(
        {"_id": ObjectId(uploader_id)},
        {"$push": {"uploads": result.inserted_id}}
    )
    
    return result.inserted_id

def get_material_by_id(material_id):
    """Retrieve a material by ID."""
    return materials.find_one({"_id": ObjectId(material_id)})

def get_materials_by_course(course_id):
    """Retrieve all materials for a specific course."""
    return list(materials.find({"course_id": ObjectId(course_id)}))

def get_materials_by_uploader(uploader_id):
    """Retrieve all materials uploaded by a specific user."""
    return list(materials.find({"uploader_id": ObjectId(uploader_id)}))

def get_recent_materials(limit=10):
    """Retrieve the most recently uploaded materials."""
    return list(materials.find().sort("upload_date", -1).limit(limit))

def search_materials(query):
    """Search for materials by keyword."""
    return list(materials.find({
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"description": {"$regex": query, "$options": "i"}},
            {"material_type": {"$regex": query, "$options": "i"}}
        ]
    }))

def update_material(material_id, update_data):
    """Update material information."""
    return materials.update_one(
        {"_id": ObjectId(material_id)},
        {"$set": update_data}
    )

def increment_download_count(material_id):
    """Increment the download count for a material."""
    return materials.update_one(
        {"_id": ObjectId(material_id)},
        {"$inc": {"downloads": 1}}
    )

def add_comment(material_id, user_id, comment_text):
    """Add a comment to a material."""
    comment = {
        "user_id": ObjectId(user_id),
        "text": comment_text,
        "date": datetime.datetime.utcnow()
    }
    return materials.update_one(
        {"_id": ObjectId(material_id)},
        {"$push": {"comments": comment}}
    )

def add_rating(material_id, user_id, rating_value):
    """Add or update a rating for a material."""
    # First check if user already rated this material
    material = materials.find_one({
        "_id": ObjectId(material_id),
        "ratings.user_id": ObjectId(user_id)
    })
    
    if material:
        # Update existing rating
        result = materials.update_one(
            {
                "_id": ObjectId(material_id),
                "ratings.user_id": ObjectId(user_id)
            },
            {"$set": {"ratings.$.value": rating_value}}
        )
    else:
        # Add new rating
        result = materials.update_one(
            {"_id": ObjectId(material_id)},
            {"$push": {"ratings": {
                "user_id": ObjectId(user_id),
                "value": rating_value
            }}}
        )
    
    # Update average rating
    update_avg_rating(material_id)
    return result

def update_avg_rating(material_id):
    """Update the average rating for a material."""
    material = materials.find_one({"_id": ObjectId(material_id)})
    if material and material.get("ratings"):
        avg = sum(r["value"] for r in material["ratings"]) / len(material["ratings"])
        return materials.update_one(
            {"_id": ObjectId(material_id)},
            {"$set": {"avg_rating": round(avg, 1)}}
        )
    return None
def get_storage_type(file_path):
    """Determine the storage type based on file path."""
    if not file_path:
        return "unknown"
    if file_path.startswith('gridfs://'):
        return "gridfs"
    if os.path.isabs(file_path) or file_path.startswith(('./','../')):
        return "local"
    return "local"

def delete_material(material_id):
    """Delete a material from the database and associated file."""
    material = get_material_by_id(material_id)
    if not material:
        return None

    file_path = material.get('file_path')
    storage_type = material.get('storage_type', 'local')
    
    if file_path:
        if storage_type == 'gridfs':
            delete_gridfs_file(file_path)
    
    decrement_materials_count(material["course_id"])
    users.update_one(
        {"_id": material["uploader_id"]},
        {"$pull": {"uploads": ObjectId(material_id)}}
    )
    users.update_many(
        {"bookmarks": ObjectId(material_id)},
        {"$pull": {"bookmarks": ObjectId(material_id)}}
    )
    
    return materials.delete_one({"_id": ObjectId(material_id)})

# Discussion-related database operations
def create_discussion(course_id, user_id, content):
    """Create a new discussion entry in the database."""
    user = get_user_by_id(user_id)
    if not user:
        return None
        
    discussion = {
        "course_id": ObjectId(course_id),
        "user_id": ObjectId(user_id),
        "user_name": user["name"],  
        "content": content,
        "date": datetime.datetime.utcnow(),
        "replies": []
    }
    result = discussions.insert_one(discussion)
    
    # Add to user's discussions
    users.update_one(
        {"_id": ObjectId(user_id)},
        {"$push": {"discussions": result.inserted_id}}
    )
    
    return result.inserted_id

def get_discussions_by_course(course_id):
    """Retrieve all discussions for a specific course."""
    return list(discussions.find({"course_id": ObjectId(course_id)}).sort("date", -1))

def get_discussions_by_user(user_id):
    """Retrieve all discussions by a specific user."""
    return list(discussions.find({"user_id": ObjectId(user_id)}).sort("date", -1))

def add_discussion(course_id, user_id, content):
    """Add a new discussion (alias for create_discussion)."""
    return create_discussion(course_id, user_id, content)

def delete_discussion(discussion_id):
    """Delete a discussion from the database."""
    discussion = discussions.find_one({"_id": ObjectId(discussion_id)})
    if discussion:
        # Remove from user's discussions
        users.update_one(
            {"_id": discussion["user_id"]},
            {"$pull": {"discussions": ObjectId(discussion_id)}}
        )
        
        # Delete the discussion
        return discussions.delete_one({"_id": ObjectId(discussion_id)})
    return None

def add_reply_to_discussion(discussion_id, user_id, content):
    """Add a reply to a discussion."""
    user = get_user_by_id(user_id)
    if not user:
        return None
        
    reply = {
        "user_id": ObjectId(user_id),
        "user_name": user["name"],
        "content": content,
        "date": datetime.datetime.utcnow()
    }
    
    return discussions.update_one(
        {"_id": ObjectId(discussion_id)},
        {"$push": {"replies": reply}}
    )

# Helper functions for data conversion
def convert_id_to_str(obj):
    """Convert ObjectId to string in a dictionary."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, ObjectId):
                obj[key] = str(value)
            elif isinstance(value, (list, dict)):
                convert_id_to_str(value)
    elif isinstance(obj, list):
        for item in obj:
            convert_id_to_str(item)
    return obj
