# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

Site for students to share course materials and help those taking the same class later.

## User stories

[Link to User Stories](https://github.com/software-students-spring2025/2-web-app-super_awesome/issues/27)

## Steps necessary to run the software

1. Prerequisites:
   - Python 3.11 or higher
   - MongoDB Atlas account

2. Clone the repository and set up virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Or create a `.env` file in the root directory with the following content:
   ```
   MONGO_URI=your_mongodb_connection_string
   SECRET_KEY=your_secret_key
   DEBUG=True
   UPLOAD_FOLDER=./uploads
   MAX_CONTENT_LENGTH=16777216
   ```

5. Run the application:
   ```bash
   python app.py
   ```

6. Access the application at `http://localhost:5001`

## Task boards

[Link to Task Board](https://github.com/orgs/software-students-spring2025/projects/112)
