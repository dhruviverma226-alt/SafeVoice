from flask import Flask, render_template, request, redirect
import sqlite3
import random
import os

app = Flask(__name__)

# Upload folders
app.config['UPLOAD_IMAGE'] = 'uploads/images'
app.config['UPLOAD_VIDEO'] = 'uploads/videos'

os.makedirs(app.config['UPLOAD_IMAGE'], exist_ok=True)
os.makedirs(app.config['UPLOAD_VIDEO'], exist_ok=True)

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint_id TEXT,
            category TEXT,
            description TEXT,
            image TEXT,
            video TEXT,
            status TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ================= HOME =================
@app.route('/')
def home():
    return render_template('index.html')

# ================= STUDENT =================
@app.route('/student', methods=['GET', 'POST'])
def student():
    if request.method == 'POST':
        category = request.form['category']
        description = request.form['description']

        image = request.files['image']
        video = request.files['video']

        image_path = ""
        video_path = ""

        # Save image
        if image:
            image_path = os.path.join(app.config['UPLOAD_IMAGE'], image.filename)
            image.save(image_path)

        # Save video
        if video:
            video_path = os.path.join(app.config['UPLOAD_VIDEO'], video.filename)
            video.save(video_path)

        complaint_id = "CMP" + str(random.randint(1000,9999))

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("""
        INSERT INTO complaints (complaint_id, category, description, image, video, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (complaint_id, category, description, image_path, video_path, "Pending"))

        conn.commit()
        conn.close()

        return f"<h2>Complaint Submitted! ID: {complaint_id}</h2><a href='/student'>Go Back</a>"

    return render_template('student.html')

# ================= TRACK =================
@app.route('/track', methods=['POST'])
def track():
    complaint_id = request.form['complaint_id']

    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM complaints WHERE complaint_id=?", (complaint_id,))
    data = c.fetchone()

    conn.close()

    if data:
        return f"<h2>Status: {data[6]}</h2><a href='/student'>Go Back</a>"
    else:
        return "<h2>Complaint not found</h2>"

# ================= ADMIN =================
@app.route('/admin')
def admin():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("SELECT * FROM complaints")
    complaints = c.fetchall()

    # Analytics
    c.execute("SELECT COUNT(*) FROM complaints")
    total = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'")
    pending = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'")
    resolved = c.fetchone()[0]

    conn.close()

    return render_template('admin.html',
                           complaints=complaints,
                           total=total,
                           pending=pending,
                           resolved=resolved)

# ================= RESOLVE =================
@app.route('/resolve/<id>')
def resolve(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute("UPDATE complaints SET status='Resolved' WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/admin')

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)