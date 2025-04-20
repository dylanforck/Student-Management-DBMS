#Dylan Forck
#Project
#Description: Student Management System - Application



# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from functools import wraps
import hashlib, uuid
from mysql_db import open_connection, close_connection, execute_query, execute_read_query

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Database config
DB_CFG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Password123!',
    'database': 'student_management'
}

def get_db_conn():
    if 'db_conn' not in g:
        g.db_conn = open_connection(**DB_CFG)
    return g.db_conn

@app.teardown_appcontext
def close_db_conn(exception=None):
    conn = g.pop('db_conn', None)
    if conn:
        close_connection(conn)

# Utilities

def hash_password(pw):
    return hashlib.md5(pw.encode()).hexdigest()

def generate_student_id():
    return str(uuid.uuid4().int)[:9]

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return wrapped

# --- Authentication ---
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
            session['role'] = res[0]['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET','POST'])
def register():
    conn = get_db_conn()
    if request.method == 'POST':
        usr = request.form['username']
        pwd = request.form['password']
        if not (usr.isalpha() and 3 <= len(usr) <= 6 and usr[0].isupper()):
            flash('Username must be 3-6 letters, first letter capitalized.', 'danger')
        else:
            if execute_read_query(conn, 'SELECT * FROM user WHERE username=%s', (usr,)):
                flash('Username already exists!', 'danger')
            else:
                execute_query(conn,
                    'INSERT INTO user (username, password) VALUES (%s, %s)',
                    (usr, hash_password(pwd))
                )
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

# --- Dashboard ---
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', username=session['username'])

# --- Student CRUD ---
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

@app.route('/students/view')
def view_students():
    conn = get_db_conn()
    students = execute_read_query(conn, 'SELECT * FROM student')
    return render_template('view_students.html', students=students)

@app.route('/students/edit/<student_id>', methods=['GET','POST'])
@admin_required
def edit_student(student_id):
    conn = get_db_conn()
    if request.method == 'POST':
        ver = int(request.form['version'])
        affected = execute_query(conn,
            '''
            UPDATE student
            SET name=%s, age=%s, gender=%s, major=%s, phone=%s, version=version+1
            WHERE id=%s AND version=%s
            ''',
            (request.form['name'], request.form['age'],
             request.form['gender'], request.form['major'],
             request.form['phone'], student_id, ver)
        )
        if affected == 0:
            flash('Concurrent modification detected. Reload and try again.', 'danger')
        else:
            flash('Student record updated!', 'success')
        return redirect(url_for('view_students'))

    rec = execute_read_query(conn, 'SELECT * FROM student WHERE id=%s', (student_id,))
    if not rec:
        flash('Student not found.', 'danger')
        return redirect(url_for('view_students'))
    return render_template('edit_student.html', student=rec[0])

@app.route('/students/delete/<student_id>', methods=['POST'])
@admin_required
def delete_student(student_id):
    conn = get_db_conn()
    execute_query(conn, 'DELETE FROM student WHERE id=%s', (student_id,))
    flash('Student deleted.', 'success')
    return redirect(url_for('view_students'))

# --- Score Query ---
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

if __name__ == '__main__':
    app.run(debug=True)

    
