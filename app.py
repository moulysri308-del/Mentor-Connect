from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this to a secure key in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mentor_connect.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'student' or 'staff'

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        # Authenticate user
        user = User.query.filter_by(email=email, role=role).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash('Login successful!', 'success')
            if role == 'student':
                return redirect(url_for('student_dashboard'))
            elif role == 'staff':
                return redirect(url_for('staff_dashboard'))
        else:
            flash('Invalid email, password, or role', 'error')
            return redirect(url_for('login'))
    return render_template('login&register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        # Hash password and create user
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=name, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('login&register.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/setting', methods=['GET', 'POST'])
def setting():
    if request.method == 'POST':
        if 'name' in request.form:  # update_profile
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            flash('Profile updated successfully', 'success')
        elif 'new_password' in request.form:  # change_password
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            if new_password == confirm_password:
                flash('Password changed successfully', 'success')
            else:
                flash('Passwords do not match', 'error')
        elif 'deactivate_account' in request.form:  # deactivate
            flash('Account deactivated', 'info')
        elif 'delete_account' in request.form:  # delete
            flash('Account deleted', 'danger')
        return redirect(url_for('setting'))
    return render_template('setting.html')

@app.route('/staff_dashboard')
def staff_dashboard():
    return render_template('staff_dashboard.html')

@app.route('/student_dashboard')
def student_dashboard():
    return render_template('student_dashboard.html')

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.name = request.form['name']
        user.email = request.form['email']
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=user)

@app.route('/find_mentors')
def find_mentors():
    if 'user_id' not in session or session.get('user_role') != 'student':
        return redirect(url_for('login'))
    # Dummy data for mentors
    mentors = [
        {'name': 'Dr. Meena R', 'subject': 'AI and Data Science'},
        {'name': 'Prof. John Doe', 'subject': 'Web Development'}
    ]
    return render_template('find_mentors.html', mentors=mentors)

@app.route('/submit_assignment', methods=['GET', 'POST'])
def submit_assignment():
    if 'user_id' not in session or session.get('user_role') != 'student':
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Dummy handling: just flash success
        flash('Assignment submitted successfully', 'success')
        return redirect(url_for('student_dashboard'))
    return render_template('submit_assignment.html')

@app.route('/manage_students')
def manage_students():
    if 'user_id' not in session or session.get('user_role') != 'staff':
        return redirect(url_for('login'))
    # Dummy data for students
    students = User.query.filter_by(role='student').all()
    return render_template('manage_students.html', students=students)

@app.route('/schedule_session', methods=['GET', 'POST'])
def schedule_session():
    if 'user_id' not in session or session.get('user_role') != 'staff':
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Dummy handling
        flash('Session scheduled successfully', 'success')
        return redirect(url_for('staff_dashboard'))
    return render_template('schedule_session.html')

@app.route('/review_assignments')
def review_assignments():
    if 'user_id' not in session or session.get('user_role') != 'staff':
        return redirect(url_for('login'))
    # Dummy data
    assignments = [{'student': 'Arun Kumar', 'assignment': 'Math Homework'}]
    return render_template('review_assignments.html', assignments=assignments)

@app.route('/view_all_sessions')
def view_all_sessions():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Dummy data
    sessions = [{'title': 'Math Mentoring', 'date': 'Sept 18'}, {'title': 'AI Workshop', 'date': 'Sept 20'}]
    return render_template('view_all_sessions.html', sessions=sessions)

@app.route('/check_all_notifications')
def check_all_notifications():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    # Dummy data
    notifications = [{'message': 'New message from Mentor John'}, {'message': 'Assignment deadline extended'}]
    return render_template('check_all_notifications.html', notifications=notifications)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
