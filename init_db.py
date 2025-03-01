from models import create_course
import pymongo
from db import courses, users, materials

# Create indexes for efficient searching
def create_indexes():
    # User indexes
    users.create_index("username", unique=True)
    users.create_index("email", unique=True)
    
    # Course indexes
    courses.create_index("course_code", unique=True)
    courses.create_index([("title", pymongo.TEXT), 
                         ("description", pymongo.TEXT), 
                         ("department", pymongo.TEXT)])
    
    # Material indexes
    materials.create_index([("title", pymongo.TEXT), 
                           ("description", pymongo.TEXT)])
    materials.create_index("course_id")
    materials.create_index("uploader_id")
    materials.create_index("material_type")
    materials.create_index("upload_date")

# Sample data for testing
def add_sample_data():
    # Sample courses
    courses_data = [
        {
            "course_code": "CS101",
            "title": "Introduction to Computer Science",
            "department": "Computer Science",
            "description": "Fundamental concepts of computer science and programming."
        },
        {
            "course_code": "MATH201",
            "title": "Calculus II",
            "department": "Mathematics",
            "description": "Advanced calculus topics including integration techniques and applications."
        },
        {
            "course_code": "PHYS150",
            "title": "Physics for Scientists and Engineers",
            "department": "Physics",
            "description": "Introductory physics for STEM majors covering mechanics and thermodynamics."
        }
    ]
    
    for course in courses_data:
        create_course(
            course["course_code"],
            course["title"],
            course["department"],
            course["description"]
        )
    
    print("Sample data added successfully!")

if __name__ == "__main__":
    print("Creating database indexes...")
    create_indexes()
    
    # Uncomment to add sample data
    # print("Adding sample data...")
    # add_sample_data()
    
    print("Database initialization complete!")