import os
import random
from functools import wraps

from dotenv import load_dotenv
from flask import (Flask, abort, flash, redirect, render_template, request,
                   url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flask_mail import Mail, Message
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.utils import secure_filename

from models import Complaint, User, db

load_dotenv()

# ================= APP CONFIG =================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///safevoice.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Uploads (kept under static so they can be served if needed)
UPLOAD_IMAGE = os.path.join('static', 'uploads', 'images')
UPLOAD_VIDEO = os.path.join('static', 'uploads', 'videos')
os.makedirs(UPLOAD_IMAGE, exist_ok=True)
os.makedirs(UPLOAD_VIDEO, exist_ok=True)

# Email (Gmail SMTP)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))

db.init_app(app)
mail = Mail(app)

login_manager = LoginManager(app)
login_manager.login_view = 'student_login'

serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
VERIFY_SALT = 'email-verify'
STATUS_STAGES = ['Submitted', 'Under Review', 'In Progress', 'Resolved']


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ================= HELPERS =================
def admin_required(view):
    """Restrict a route to logged-in administrators."""
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def student_required(view):
    """Restrict a route to logged-in, verified students."""
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.role != 'student':
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def send_verification_email(user):
    token = serializer.dumps(user.email, salt=VERIFY_SALT)
    link = url_for('verify_email', token=token, _external=True)
    msg = Message('Verify your SafeVoice account', recipients=[user.email])
    msg.body = (
        f"Welcome to SafeVoice.\n\n"
        f"Please verify your email by clicking the link below:\n{link}\n\n"
        f"This link expires in 24 hours. If you did not sign up, ignore this email."
    )
    mail.send(msg)


def save_upload(file_storage, folder):
    if file_storage and file_storage.filename:
        filename = secure_filename(file_storage.filename)
        path = os.path.join(folder, filename)
        file_storage.save(path)
        return path
    return ''


# ================= HOME =================
@app.route('/')
def home():
    return render_template('index.html')


# ================= STUDENT AUTH =================
@app.route('/student/register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('That email is already registered.', 'error')
            return redirect(url_for('student_register'))

        user = User(email=email, role='student', is_verified=False)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        try:
            send_verification_email(user)
        except Exception:
            flash('Could not send the verification email. Check mail settings.', 'error')
            return redirect(url_for('student_register'))

        flash('Registration successful! Check your email for the verification link.', 'success')
        return redirect(url_for('student_login'))

    return render_template('student_register.html')


@app.route('/verify/<token>')
def verify_email(token):
    try:
        email = serializer.loads(token, salt=VERIFY_SALT, max_age=86400)
    except SignatureExpired:
        flash('That verification link has expired.', 'error')
        return redirect(url_for('student_register'))
    except BadSignature:
        flash('Invalid verification link.', 'error')
        return redirect(url_for('student_register'))

    user = User.query.filter_by(email=email).first()
    if user and not user.is_verified:
        user.is_verified = True
        db.session.commit()
    flash('Email verified! You can now log in.', 'success')
    return redirect(url_for('student_login'))


@app.route('/student/login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email, role='student').first()

        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('student_login'))
        if not user.is_verified:
            flash('Please verify your email before logging in.', 'error')
            return redirect(url_for('student_login'))

        login_user(user)
        return redirect(url_for('student_dashboard'))

    return render_template('student_login.html')


# ================= STUDENT DASHBOARD =================
@app.route('/student/dashboard', methods=['GET', 'POST'])
@student_required
def student_dashboard():
    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']
        image_path = save_upload(request.files.get('image'), UPLOAD_IMAGE)
        video_path = save_upload(request.files.get('video'), UPLOAD_VIDEO)

        complaint_id = 'CMP' + str(random.randint(100000, 999999))
        complaint = Complaint(
            complaint_id=complaint_id,
            category=category,
            description=description,
            image=image_path,
            video=video_path,
            status='Submitted',
        )
        db.session.add(complaint)
        db.session.commit()

        flash(f'Complaint submitted anonymously! Your tracking ID is {complaint_id}', 'success')
        return redirect(url_for('student_dashboard'))

    return render_template('student_dashboard.html')


@app.route('/track', methods=['POST'])
@student_required
def track():
    complaint_id = request.form['complaint_id'].strip()
    complaint = Complaint.query.filter_by(complaint_id=complaint_id).first()
    if complaint:
        flash(f'Complaint {complaint_id} status: {complaint.status}', 'success')
    else:
        flash('No complaint found with that ID.', 'error')
    return redirect(url_for('student_dashboard'))


# ================= ADMIN AUTH =================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']
        user = User.query.filter_by(email=email, role='admin').first()

        if not user or not user.check_password(password):
            flash('Invalid admin credentials.', 'error')
            return redirect(url_for('admin_login'))

        login_user(user)
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')


# ================= ADMIN DASHBOARD =================
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    total = len(complaints)
    pending = sum(1 for c in complaints if c.status != 'Resolved')
    resolved = sum(1 for c in complaints if c.status == 'Resolved')
    return render_template(
        'admin_dashboard.html',
        complaints=complaints,
        total=total,
        pending=pending,
        resolved=resolved,
        stages=STATUS_STAGES,
    )


@app.route('/admin/update/<int:complaint_id>', methods=['POST'])
@admin_required
def update_status(complaint_id):
    complaint = db.session.get(Complaint, complaint_id)
    if complaint:
        new_status = request.form['status']
        if new_status in STATUS_STAGES:
            complaint.status = new_status
            db.session.commit()
            flash('Status updated.', 'success')
    return redirect(url_for('admin_dashboard'))


# ================= LOGOUT =================
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


# ================= STARTUP =================
def seed_admin():
    """Create the administrator account from environment variables if missing."""
    admin_email = os.getenv('ADMIN_EMAIL')
    admin_password = os.getenv('ADMIN_PASSWORD')
    if not admin_email or not admin_password:
        return
    admin_email = admin_email.strip().lower()
    if not User.query.filter_by(email=admin_email).first():
        admin = User(email=admin_email, role='admin', is_verified=True)
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()


with app.app_context():
    db.create_all()
    seed_admin()


if __name__ == '__main__':
    app.run(debug=True)
