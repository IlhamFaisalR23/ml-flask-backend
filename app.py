from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_cors import CORS
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, auth
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
CORS(app)

# Firebase Admin SDK initialization
cred = credentials.Certificate('roblocks-rbc-firebase-adminsdk-fbsvc-a00ea47599.json')
firebase_admin.initialize_app(cred)

# Konfigurasi MySQL menggunakan environment variables
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB', 'roblock_module')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Secret key for session management
app.secret_key = 'kunci rahasia'

mysql = MySQL(app)

def execute_query(query, args=None, fetch_one=False, commit=False):
    cur = mysql.connection.cursor()
    cur.execute(query, args)
    if commit:
        mysql.connection.commit()
    result = cur.fetchone() if fetch_one else cur.fetchall()
    cur.close()
    return result

# ---------------- API MODULE DAN QUIZ UNTUK APLIKASI ANDROID ----------------
@app.route('/api/modules', methods=['GET'])
def api_get_all_modules():
    query = "SELECT * FROM module_table"
    modules = execute_query(query)
    return jsonify(modules)

@app.route('/api/modules/<module_id>', methods=['GET'])
def api_get_module(module_id):
    query = "SELECT * FROM module_table WHERE id = %s"
    module = execute_query(query, (module_id,), fetch_one=True)
    if module:
        return jsonify(module)
    return jsonify({"error": "Module not found"}), 404

@app.route('/api/modules/<module_id>/questions', methods=['GET'])
def api_get_module_questions(module_id):
    query = "SELECT * FROM question_table WHERE module_id = %s"
    questions = execute_query(query, (module_id,))
    return jsonify(questions)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- AUTHENTICATION ROUTES ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = execute_query("SELECT * FROM users WHERE email = %s", (email,), fetch_one=True)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        # Cek apakah email sudah ada
        existing_user = execute_query("SELECT * FROM users WHERE email = %s", (email,), fetch_one=True)
        if existing_user:
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('register'))
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Tambah user baru
        query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
        execute_query(query, (name, email, hashed_password), commit=True)
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ---------------- PROTECTED ROUTES ----------------
@app.route('/')
def landing_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template("index.html")

@app.route('/dashboard')
@login_required
def dashboard():
    query = "SELECT COUNT(*) as total_modules FROM module_table"
    result = execute_query(query, fetch_one=True)
    total_modules = result['total_modules'] if result else 0
    return render_template('dashboard.html', total_modules=total_modules)

@app.route('/modules')
@login_required
def manage_modules():
    query = "SELECT * FROM module_table"
    modules = execute_query(query)
    return render_template('modules.html', modules=modules)

@app.route('/modules/create', methods=['GET', 'POST'])
@login_required
def create_module():
    if request.method == 'POST':
        data = request.form
        query = """
            INSERT INTO module_table 
            (id, title, description, created_at, updated_at, link_video) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        timestamp = int(datetime.now().timestamp() * 1000)
        args = (
            data['id'], data['title'], data['description'], 
            timestamp, timestamp, data['link_video']
        )
        execute_query(query, args, commit=True)
        return redirect(url_for('manage_modules'))
    return render_template('create_module.html')

@app.route('/modules/<module_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_module(module_id):
    if request.method == 'POST':
        data = request.form
        query = """
            UPDATE module_table 
            SET title = %s, description = %s, updated_at = %s, link_video = %s
            WHERE id = %s
        """
        timestamp = int(datetime.now().timestamp() * 1000)
        args = (
            data['title'], data['description'], 
            timestamp, data['link_video'], module_id
        )
        execute_query(query, args, commit=True)
        return redirect(url_for('manage_modules'))
    
    query = "SELECT * FROM module_table WHERE id = %s"
    module = execute_query(query, (module_id,), fetch_one=True)
    if not module:
        return "Module not found", 404
    return render_template('edit_module.html', module=module)

@app.route('/modules/<module_id>/delete', methods=['POST'])
@login_required
def delete_module(module_id):
    query = "DELETE FROM module_table WHERE id = %s"
    execute_query(query, (module_id,), commit=True)
    return redirect(url_for('manage_modules'))

@app.route('/modules/<module_id>/questions')
@login_required
def manage_questions(module_id):
    module_query = "SELECT * FROM module_table WHERE id = %s"
    module = execute_query(module_query, (module_id,), fetch_one=True)
    if not module:
        return "Module not found", 404
    
    questions_query = "SELECT * FROM question_table WHERE module_id = %s"
    questions = execute_query(questions_query, (module_id,))
    
    return render_template('questions.html', module=module, questions=questions)

@app.route('/modules/<module_id>/questions/create', methods=['GET', 'POST'])
@login_required
def create_question(module_id):
    if request.method == 'POST':
        data = request.form
        query = """
            INSERT INTO question_table 
            (id, module_id, question_text, option_a, option_b, option_c, option_d, correct_answer, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        timestamp = int(datetime.now().timestamp() * 1000)
        args = (
            data['id'], module_id, data['question_text'],
            data['option_a'], data['option_b'], data['option_c'], data['option_d'],
            data['correct_answer'], timestamp, timestamp
        )
        execute_query(query, args, commit=True)
        return redirect(url_for('manage_questions', module_id=module_id))
    
    return render_template('create_question.html', module_id=module_id)

@app.route('/questions/<question_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    if request.method == 'POST':
        data = request.form
        query = """
            UPDATE question_table 
            SET question_text = %s, option_a = %s, option_b = %s, 
                option_c = %s, option_d = %s, correct_answer = %s, updated_at = %s
            WHERE id = %s
        """
        timestamp = int(datetime.now().timestamp() * 1000)
        args = (
            data['question_text'], data['option_a'], data['option_b'],
            data['option_c'], data['option_d'], data['correct_answer'],
            timestamp, question_id
        )
        execute_query(query, args, commit=True)
        
        module_query = "SELECT module_id FROM question_table WHERE id = %s"
        question = execute_query(module_query, (question_id,), fetch_one=True)
        return redirect(url_for('manage_questions', module_id=question['module_id']))
    
    query = "SELECT * FROM question_table WHERE id = %s"
    question = execute_query(query, (question_id,), fetch_one=True)
    if not question:
        return "Question not found", 404
    return render_template('edit_question.html', question=question)

@app.route('/questions/<question_id>/delete', methods=['POST'])
@login_required
def delete_question(question_id):
    module_query = "SELECT module_id FROM question_table WHERE id = %s"
    question = execute_query(module_query, (question_id,), fetch_one=True)
    
    query = "DELETE FROM question_table WHERE id = %s"
    execute_query(query, (question_id,), commit=True)
    
    return redirect(url_for('manage_questions', module_id=question['module_id']))

# ---------------- MISC ----------------
@app.route("/ping", methods=["GET"])
def ping():
    return "pong!"

@app.route('/test', methods=['GET'])
def test():
    return "Server is running!"

# ---------------- USER MANAGEMENT ROUTES ----------------
@app.route('/users')
def manage_users():
    try:
        # Get all users from Firebase
        users = auth.list_users().iterate_all()
        user_list = []
        for user in users:
            user_list.append({
                'uid': user.uid,
                'email': user.email
            })
        return render_template('manage_user.html', users=user_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = auth.list_users().iterate_all()
        user_list = []
        for user in users:
            user_list.append({
                'uid': user.uid,
                'email': user.email
            })
        return jsonify(user_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<uid>', methods=['GET'])
def get_user(uid):
    try:
        user = auth.get_user(uid)
        return jsonify({
            'uid': user.uid,
            'email': user.email
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        user = auth.create_user(
            email=data.get('email'),
            password=data.get('password')
        )
        return jsonify({
            'uid': user.uid,
            'email': user.email
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/users/<uid>', methods=['DELETE'])
def delete_user(uid):
    try:
        auth.delete_user(uid)
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
