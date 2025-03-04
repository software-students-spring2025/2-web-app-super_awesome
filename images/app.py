from flask import Flask, render_template, request, redirect, url_for, send_file, session, flash
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from bson.objectid import ObjectId
from dotenv import load_dotenv
from database import (
    create_user, get_user_by_email, get_user_by_id,
    create_course, get_all_courses, get_course_by_id,
    create_material, get_materials_by_course, get_materials_by_uploader,
    get_material_by_id, delete_material as delete_material_db,
    add_discussion, get_discussions_by_course, get_discussions_by_user, update_user,
    get_user_by_username, search_courses
)

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.jinja_env.globals.update(str=str)  # Allow use of str() in templates

# Configure Flask application
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', './uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# (For demo purposes; in production courses come from the DB)
users = {}
courses = [
    {"id": 1, "code": "CS101", "name": "Introduction to Computer Science", "instructor": "Dr. Smith"},
    {"id": 2, "code": "MATH201", "name": "Calculus I", "instructor": "Dr. Johnson"},
    {"id": 3, "code": "ENG102", "name": "English Composition", "instructor": "Prof. Williams"}
]
materials = []
discussions = []

# ---------------------------
# Authentication and Profile Routes
# ---------------------------
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            return redirect(url_for('courses'))
        return render_template("login.html", error="Invalid email or password")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        if get_user_by_username(name):
            return render_template("register.html", error="Username already taken")
        if get_user_by_email(email):
            return render_template("register.html", error="Email already registered")
        user_id = create_user(name, email, password)
        if user_id:
            session['user_id'] = str(user_id)
            return redirect(url_for('courses'))
        return render_template("register.html", error="Registration failed")
    return render_template("register.html")

@app.route("/profile")
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    user_materials = get_materials_by_uploader(user_id)
    user_discussions = get_discussions_by_user(user_id)
    return render_template("profile.html", user=user, materials=user_materials, discussions=user_discussions)

@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# ---------------------------
# Courses and Material Management Routes
# ---------------------------
@app.route('/courses')
def courses():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    all_courses = get_all_courses()
    return render_template('courses.html', courses=all_courses)

@app.route('/courses/create', methods=['GET', 'POST'])
def create_course_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        try:
            course_code = request.form.get('code', '').strip()
            title = request.form.get('name', '').strip()
            department = request.form.get('department', '').strip() or None
            description = request.form.get('description', '').strip() or None
            instructor = request.form.get('instructor', '').strip() or None
            if not course_code:
                return render_template('create_course.html', error="Course code is required", form_data=request.form)
            if not title:
                return render_template('create_course.html', error="Course name is required", form_data=request.form)
            course_id = create_course(course_code, title, department, description, instructor)
            if course_id:
                return redirect(url_for('courses'))
            return render_template('create_course.html', error="Failed to create course", form_data=request.form)
        except Exception as e:
            app.logger.error(f"Error creating course: {str(e)}")
            return render_template('create_course.html', error="An error occurred while creating the course", form_data=request.form)
    return render_template('create_course.html')

@app.route('/courses/<course_id>')
def course_detail(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    course = get_course_by_id(course_id)
    if not course:
        return "Course not found", 404
    course_materials = get_materials_by_course(course_id)
    course_discussions = get_discussions_by_course(course_id)
    return render_template('course_detail.html', course=course, materials=course_materials, discussions=course_discussions)

@app.route('/courses/<course_id>/upload', methods=['POST'])
def upload_material(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if 'material' not in request.files:
        return 'No file uploaded'
    file = request.files['material']
    if file.filename == '':
        return 'No file selected'
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        title = request.form.get('title', filename)
        description = request.form.get('description', 'Uploaded on ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        material_id = create_material(title=title, description=description, course_id=course_id,
                                      uploader_id=session['user_id'], file_path=file_path, material_type='document')
        if not material_id:
            os.remove(file_path)
            return 'Failed to create material'
    return redirect(url_for('course_detail', course_id=course_id))

@app.route('/materials/<material_id>/download')
def download_material(material_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    material = get_material_by_id(material_id)
    if not material:
        return 'Material not found', 404
    return send_file(material['file_path'], as_attachment=True, download_name=os.path.basename(material['file_path']))

@app.route('/materials/<material_id>/delete', methods=['POST'])
def delete_material(material_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    material = get_material_by_id(material_id)
    if not material:
        return 'Material not found', 404
    if str(material['uploader_id']) != session['user_id']:
        return 'Unauthorized', 403
    try:
        os.remove(material['file_path'])
    except OSError:
        pass
    delete_material_db(material_id)
    return redirect(request.referrer or url_for('profile'))

@app.route('/courses/<course_id>/discussions', methods=['POST'])
def add_discussion_route(course_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    content = request.form.get('content')
    if not content:
        return 'Discussion content is required'
    discussion_id = add_discussion(course_id, session['user_id'], content)
    if not discussion_id:
        return 'Failed to create discussion'
    return redirect(url_for('course_detail', course_id=course_id))

# ---------------------------
# Edit Profile Route
# ---------------------------
@app.route("/edit-profile", methods=["GET", "POST"])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    user = get_user_by_id(user_id)
    if request.method == "POST":
        new_name = request.form.get("name", "").strip()
        new_password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        update_data = {}
        if new_name and new_name != user['name']:
            update_data['name'] = new_name
        if new_password:
            if new_password != confirm_password:
                flash("Passwords do not match!", "error")
                return render_template("edit_profile.html", user=user)
            update_data['password'] = generate_password_hash(new_password)
        if update_data:
            update_user(user_id, update_data)
            flash("Profile updated successfully!", "success")
            return redirect(url_for("profile"))
        flash("No changes were made.", "info")
    return render_template("edit_profile.html", user=user)

# New route to serve uploaded files (if needed)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# New Search Route for Courses

@app.route('/search', methods=['GET'])
def search_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # For simplicity, return all courses from the database (client-side filtering will be applied)
    courses_result = get_all_courses()
    return render_template('search.html', courses=courses_result, query="")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
