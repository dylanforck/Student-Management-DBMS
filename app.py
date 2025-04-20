# app.py
# Author: Dylan Forck

'''
Student Management System - Main Flask Application
'''

# Standard library imports
import os
from urllib.parse import urlparse
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
import hashlib, uuid
from mysql_db import open_connection, close_connection, execute_query, execute_read_query


# Initialize Flask app
app = Flask(__name__)

# Set secret key for session management
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'super_secret_key')



# DATABASE CONFIGURATION
# Supports Railway-style full URL or individual env vars
if 'MYSQL_URL' in os.environ:
    # Preferred format: single MySQL connection URL
    _url = urlparse(os.environ['MYSQL_URL'])
    DB_CFG = {
        'host':     _url.hostname,
        'user':     _url.username,
        'password': _url.password,
        'database': _url.path.lstrip('/'),
        'port':     _url.port or 3306
    }
else:
    # Fallback if split env vars are provided instead
    DB_CFG = {
        'host':     os.environ.get('MYSQLHOST'),
        'port':     int(os.environ.get('MYSQLPORT', 3306)),
        'user':     os.environ.get('MYSQLUSER'),
        'password': os.environ.get('MYSQLPASSWORD') or os.environ.get('MYSQL_ROOT_PASSWORD'),
        'database': os.environ.get('MYSQLDATABASE') or os.environ.get('MYSQL_DATABASE'),
    }

# Establish and return a per-request database connection (stored in Flask `g`)
def get_db_conn():
    if 'db_conn' not in g:
        g.db_conn = open_connection(
             host_name     = DB_CFG['host'],
             user_name     = DB_CFG['user'],
             user_password = DB_CFG['password'],
             db_name       = DB_CFG['database'],
             port          = DB_CFG.get('port', 3306)
         )
        if g.db_conn is None:
            raise RuntimeError(
                f"Could not connect to database with config: {DB_CFG}"
            )
    return g.db_conn

# Clean up and close DB connection after the request is handled
@app.teardown_appcontext
def close_db_conn(exception=None):

    conn = g.pop('db_conn', None)
    if conn:
        close_connection(conn)



# HELPER FUNCTIONS
# Return MD5 hash of given plaintext password
def hash_password(pw):
    return hashlib.md5(pw.encode()).hexdigest()

# Generate a unique 9-digit student ID
def generate_student_id():
    return str(uuid.uuid4().int)[:9]



# AUTHENTICATION ROUTES
# Authenticate user and start session
@app.route('/login', methods=['GET','POST'])
def login():
    conn = get_db_conn()
    if request.method == 'POST':
        usr = request.form['username']
        pwd = hash_password(request.form['password'])
        res = execute_read_query(conn,
            'SELECT username, role FROM user WHERE username=%s AND password=%s',
            (usr, pwd)
        )
        if res:
            session['username'] = usr
            session['role']     = res[0].get('role', 'user')
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

# Allow new user to register (default role is user)
@app.route('/register', methods=['GET','POST'])
def register():
    conn = get_db_conn()
    if request.method == 'POST':
        usr = request.form['username']
        pwd = request.form['password']
        if not (usr.isalpha() and 3 <= len(usr) <= 6 and usr[0].isupper()):
            flash('Username must be 3-6 letters, first letter capitalized.', 'danger')
        elif execute_read_query(conn, 'SELECT 1 FROM user WHERE username=%s', (usr,)):
            flash('Username already exists!', 'danger')
        else:
            execute_query(conn,
                'INSERT INTO user (username, password) VALUES (%s, %s)',
                (usr, hash_password(pwd))
            )
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')

# Logout user and clear session
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))



# DASHBOARD ROUTES
# Root URL — redirect to dashboard
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

# Show dashboard if user is logged in
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])



# DECORATOR FOR ADMIN-ONLY ACCESS
from functools import wraps

# Restrict route access to users with admin role
def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return wrapped



# STUDENT CRUD ROUTES
# Admin can add new student records
@app.route('/students/add', methods=['GET','POST'])
@admin_required
def add_student():
    conn = get_db_conn()
    if request.method=='POST':
        sid = generate_student_id()
        execute_query(conn,
            'INSERT INTO student (id,name,age,gender,major,phone) VALUES (%s,%s,%s,%s,%s,%s)',
            (sid, request.form['name'], request.form['age'],
             request.form['gender'], request.form['major'], request.form['phone'])
        )
        flash('Student added!', 'success')
        return redirect(url_for('view_students'))
    return render_template('add_student.html')

# Show all student records to any logged-in user
@app.route('/students/view')
def view_students():
    conn = get_db_conn()
    students = execute_read_query(conn, 'SELECT * FROM student')
    return render_template('view_students.html', students=students)

# Admin can edit a student record, uses version field for optimistic locking
@app.route('/students/edit/<student_id>', methods=['GET','POST'])
@admin_required
def edit_student(student_id):
    conn = get_db_conn()
    if request.method == 'POST':
        old_ver = int(request.form['version'])
        affected = execute_query(conn, '''
            UPDATE student
            SET name=%s,
                age=%s,
                gender=%s,
                major=%s,
                phone=%s,
                version=version+1
            WHERE id=%s AND version=%s
        ''', (
            request.form['name'],
            request.form['age'],
            request.form['gender'],
            request.form['major'],
            request.form['phone'],
            student_id,
            old_ver
        ))
        if affected == 0:
            flash('Concurrent modification detected. Please reload and try again.', 'danger')
        else:
            flash('Student record updated!', 'success')
        return redirect(url_for('view_students'))

    # Show edit form with current data on GET
    rec = execute_read_query(conn,
        'SELECT id,name,age,gender,major,phone,version FROM student WHERE id=%s',
        (student_id,)
    )
    if not rec:
        flash('Student not found.', 'danger')
        return redirect(url_for('view_students'))
    return render_template('edit_student.html', student=rec[0])

# Admin can delete student records
@app.route('/students/delete/<student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    conn = get_db_conn()
    execute_query(conn, 'DELETE FROM student WHERE id=%s', (student_id,))
    flash('Student deleted.', 'success')
    return redirect(url_for('view_students'))



# SCORE QUERY ROUTE
# Users can search for a student's scores by name
@app.route('/scores/query')
def query_scores():
    conn = get_db_conn()
    name = request.args.get('student_name','')
    scores = None
    if name:
        scores = execute_read_query(conn,
            '''
            SELECT s.id, s.name, c.course_id, c.course_name, sc.score
            FROM student s
            JOIN score sc ON s.id=sc.student_id
            JOIN course c ON sc.course_id=c.course_id
            WHERE s.name=%s
            ''', (name,)
        )
    return render_template('query_scores.html', scores=scores, student_name=name)



# ENTRY POINT
# Run the Flask dev server
if __name__ == '__main__':
    app.run(debug=True)

