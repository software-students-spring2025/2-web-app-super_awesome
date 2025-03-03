# This file makes the database directory a Python package
from .models import (
    create_user, get_user_by_email, get_user_by_id,
    create_course, get_all_courses, get_course_by_id,
    create_material, get_materials_by_course, get_materials_by_uploader,
    get_material_by_id, delete_material,
    add_discussion, get_discussions_by_course, get_discussions_by_user
)

__all__ = [
    'create_user', 'get_user_by_email', 'get_user_by_id',
    'create_course', 'get_all_courses', 'get_course_by_id',
    'create_material', 'get_materials_by_course', 'get_materials_by_uploader',
    'get_material_by_id', 'delete_material',
    'add_discussion', 'get_discussions_by_course', 'get_discussions_by_user'
] 