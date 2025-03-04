import unittest
from bson.objectid import ObjectId
import models
from db import users, courses, materials

class TestDatabase(unittest.TestCase):
    def setUp(self):
        users.delete_many({})
        courses.delete_many({})
        materials.delete_many({})
    
    def test_user_operations(self):
        # Create a user
        user_id = models.create_user("testuser", "test@example.com", "password123")
        self.assertIsNotNone(user_id)
        
        # Get user by username
        user = models.get_user_by_username("testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user["email"], "test@example.com")
        
        # Update user
        models.update_user(user_id, {"email": "updated@example.com"})
        user = models.get_user_by_id(user_id)
        self.assertEqual(user["email"], "updated@example.com")
    
    def test_course_operations(self):
        # Create a course
        course_id = models.create_course("TEST101", "Test Course", "Testing", "A course for testing")
        self.assertIsNotNone(course_id)
        
        # Get course by code
        course = models.get_course_by_code("TEST101")
        self.assertIsNotNone(course)
        self.assertEqual(course["title"], "Test Course")
        
        # Search courses
        results = models.search_courses("test")
        self.assertEqual(len(results), 1)
    
    def test_material_operations(self):
        # Create test user and course first
        user_id = models.create_user("materialuser", "material@example.com", "password")
        course_id = models.create_course("MAT101", "Material Test", "Testing", "Testing materials")
        
        # Create material
        material_id = models.create_material(
            "Test Notes", 
            "These are test notes", 
            course_id, 
            user_id, 
            "/uploads/test.pdf", 
            "notes"
        )
        self.assertIsNotNone(material_id)
        
        # Get materials by course
        materials = models.get_materials_by_course(course_id)
        self.assertEqual(len(materials), 1)
        
        # Test rating system
        models.add_rating(material_id, user_id, 4)
        material = models.get_material_by_id(material_id)
        self.assertEqual(material["avg_rating"], 4)
        
        # Test comment system
        models.add_comment(material_id, user_id, "Test comment")
        material = models.get_material_by_id(material_id)
        self.assertEqual(len(material["comments"]), 1)
        
        # Test delete material
        models.delete_material(material_id)
        material = models.get_material_by_id(material_id)
        self.assertIsNone(material)
        
        # Check that course count was decremented
        course = models.get_course_by_id(course_id)
        self.assertEqual(course["materials_count"], 0)

if __name__ == "__main__":
    unittest.main()
