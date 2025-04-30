# Student-Management-DBMS
Student Management DBMS

A simple Flask + MySQL web application for managing student records, with role‑based access control (Admin vs. User).

## Table of Contents

1. [Features](#features)  
2. [Requirements](#requirements)  
3. [Setup & Local Development](#setup--local-development)  
4. [Environment Variables](#environment-variables)  
5. [Running the App](#running-the-app)  
6. [Deployment](#deployment)  
7. [Test Accounts](#test-accounts)  
8. [Project Structure](#project-structure)  
9. [Database Model](#database-model) 

## Features

- User registration & login with MD5‑hashed passwords  
- Role‑based access:  
  - **Admin** can add, edit, delete students  
  - **User** can view students and query scores  
- Student CRUD (Create, Read, Update, Delete)  
- Query student scores across courses  
- Configurable via environment variables for easy local/remote deployment

## Requirements

- **Python**: 3.8+  
- **pip** (Python package manager)  
- **MySQL** server (Railway‑hosted or local)  

Python packages (install via `requirements.txt`):

```bash
flask
mysql-connector-python
```

## Setup & Local Development

1. **Clone the repo**  
```bash
git clone https://github.com/dylanforck/Student‑Management‑DBMS.git
cd Student‑Management‑DBMS
```

2. **Create & activate a virtual environment**  
```bash
python3 -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows
```

3. **Install Python dependencies**  
```bash
pip install -r requirements.txt
```

4. **Initialize the MySQL database**  
```sql
CREATE DATABASE student_management;

USE student_management;

CREATE TABLE user (
  username VARCHAR(32) PRIMARY KEY,
  password VARCHAR(32) NOT NULL,
  role ENUM('admin','user') NOT NULL DEFAULT 'user'
);

CREATE TABLE student (
  id VARCHAR(9) PRIMARY KEY,
  name VARCHAR(32) NOT NULL,
  age INT,
  gender CHAR(1),
  major VARCHAR(32),
  phone VARCHAR(32),
  version INT NOT NULL DEFAULT 1
);

CREATE TABLE course (
  course_id VARCHAR(32) PRIMARY KEY,
  course_name VARCHAR(64) NOT NULL
);

CREATE TABLE score (
  student_id VARCHAR(9),
  course_id VARCHAR(32),
  score INT,
  PRIMARY KEY (student_id, course_id),
  FOREIGN KEY (student_id) REFERENCES student(id) ON DELETE CASCADE,
  FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE
);
```

## Environment Variables

The app reads configuration from environment variables:

- **`FLASK_SECRET_KEY`**  
  Secret key for sessions (defaults to `super_secret_key` if unset).

- **`MYSQL_URL`** _(preferred)_  
  A full connection string, e.g.:  
  ```
  mysql://user:password@hostname:3306/student_management
  ```

- **OR**, if you don’t use `MYSQL_URL`, set these instead:  
  - `MYSQLHOST`  
  - `MYSQLPORT` (defaults to `3306`)  
  - `MYSQLUSER`  
  - `MYSQLPASSWORD` _or_ `MYSQL_ROOT_PASSWORD`  
  - `MYSQLDATABASE` _or_ `MYSQL_DATABASE`

## Running the App

With the virtualenv active and env vars set:

```bash
# Option A: Flask’s development server
export FLASK_APP=app.py
export FLASK_ENV=development
flask run

# Option B: Directly via Python
python app.py
```

Visit <http://127.0.0.1:5000> in your browser.

## Deployment

### Railway

1. Push the code to GitHub (include `requirements.txt`, `Procfile`, `templates/`, etc.).  
2. In Railway’s dashboard, link the repo and set the same env vars (`FLASK_SECRET_KEY`, `MYSQL_URL`, etc.).  
3. Ensure the `Procfile` contains:
   ```
   web: gunicorn app:app
   ```
4. Trigger a deploy—Railway will install dependencies, use the Procfile, and give you a live URL.

Hosted on Railway at  
  https://student-management-dbms-production.up.railway.app

## Test Accounts

> **Note:** registration via the UI always creates a `role='user'`. To get an **admin** account, insert one manually:

```sql
INSERT INTO user (username, password, role)
VALUES (
  'Admin',
  MD5('Admin123!'),
  'admin'
);
```

- **Admin** → username: `Admin` | password: `Admin123!`  
- **User**  → username: `User`  | password: `User123!`  
- **Other** → register through the UI with any valid username (3–6 letters, first capitalized) and password; will have `role='user'`.

## Project Structure

```
Student-Management-DBMS/
├── app.py              # Main Flask application
├── mysql_db.py         # MySQL connection & helper functions
├── database_schema.sql # MySQL database table schema
├── mock_table_data.sql # Used to load mock sql table data
├── requirements.txt    # Python dependencies
├── Procfile            # web: gunicorn app:app
├── README.md           # This documentation
└── templates/
    ├── base.html
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── add_student.html
    ├── view_students.html
    ├── edit_student.html
    └── query_scores.html
```

## Database Model

Below is the Entity–Relationship diagram for the Student Management System:

![ER Diagram](docs/er_diagram.png)