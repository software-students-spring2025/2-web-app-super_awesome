from .models import create_course
import pymongo
from .db import courses, users, materials, discussions

# Create indexes for efficient searching
def create_indexes():
    # User indexes
    users.create_index("username", unique=True)
    users.create_index("email", unique=True)
    
    # Course indexes
    courses.create_index("code", unique=True)
    courses.create_index([("name", pymongo.TEXT), 
                         ("description", pymongo.TEXT), 
                         ("department", pymongo.TEXT)])
    
    # Material indexes
    materials.create_index([("name", pymongo.TEXT), 
                           ("description", pymongo.TEXT)])
    materials.create_index("course_id")
    materials.create_index("uploader_id")
    materials.create_index("material_type")
    materials.create_index("upload_date")
    
    # Discussion indexes
    discussions.create_index("course_id")
    discussions.create_index("user_id")
    discussions.create_index("date")
    discussions.create_index([("content", pymongo.TEXT)])

# Sample data for testing
def add_sample_data():
    # Sample courses
    courses_data = [
        {
            "code": "CS101",
            "name": "Introduction to Computer Science",
            "department": "Computer Science",
            "description": "Fundamental concepts of computer science and programming.",
            "instructor": "Dr. Smith"
        },
        {
            "code": "MATH201",
            "name": "Calculus II",
            "department": "Mathematics",
            "description": "Advanced calculus topics including integration techniques and applications.",
            "instructor": "Dr. Johnson"
        },
        {
            "code": "PHYS150",
            "name": "Physics for Scientists and Engineers",
            "department": "Physics",
            "description": "Introductory physics for STEM majors covering mechanics and thermodynamics.",
            "instructor": "Prof. Williams"
        }
    ]
    
    for course in courses_data:
        create_course(
            course["code"],
            course["name"],
            course["department"],
            course["description"],
            course["instructor"]
        )
    
    print("Sample data added successfully!")

if __name__ == "__main__":
    print("Creating database indexes...")
    create_indexes()
    
    
    print("Database initialization complete!")
