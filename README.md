Safe Voice is a secure and anonymous complaint management system designed for colleges. It enables students to report issues such as harassment, bullying, ragging, infrastructure problems, or other concerns without revealing their identity. The platform promotes a safer campus environment by ensuring confidentiality while allowing administrators to efficiently manage and resolve complaints.

## Key Features:

Anonymous Complaint Submission: Students can submit complaints without disclosing their identity.
Media Upload Support: Users can attach photos and videos as evidence to strengthen their complaints.
Complaint Tracking: Students receive a unique complaint ID to track the status of their submission.
Admin Dashboard: Administrators can view, categorize, prioritize, and manage complaints through an interactive dashboard.
Status Updates: Complaints move through stages such as Submitted, Under Review, In Progress, and Resolved.
Analytics Dashboard: Displays complaint statistics, trends, categories, and resolution rates to help college authorities identify recurring issues.
Secure Data Management: Complaint data and uploaded media are stored securely to protect user privacy.

## Tech Stacks: 

Frontend
HTML5
CSS3
JavaScript
Jinja2 Templates (Flask templating engine)

Backend
Python
Flask Framework

Database
SQLite (accessed through the SQLAlchemy ORM)

Authentication & Security
Separate student and admin login portals
Email verification for student sign-up (Gmail SMTP)
Hashed passwords (Werkzeug) and signed verification tokens (itsdangerous)
Role-protected routes via Flask-Login
Complaints are never linked to a user, so student identity stays anonymous

Libraries & Modules
Flask, Flask-SQLAlchemy, Flask-Login, Flask-Mail
python-dotenv (environment configuration)
Random (for generating anonymous complaint IDs)
OS (for file handling and uploads)

## Problem Statement: 
Many students hesitate to report sensitive issues due to fear of retaliation or exposure. Traditional complaint systems often lack anonymity, transparency, and efficient tracking, resulting in underreporting and delayed resolutions.

## Solution: 
Safe Voice addresses these challenges by providing an anonymous digital platform where students can safely report incidents, upload supporting evidence, track complaint progress, and enable administrators to monitor and resolve issues efficiently through a centralized dashboard.

## Expected Impact
Encourages students to report issues without fear.
Improves transparency in complaint handling.
Reduces response time for administrators.
Provides data-driven insights for better campus management.
Creates a safer and more accountable college environment.

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/SafeVoice.git
```

### 2. Navigate to the project folder

```bash
cd SafeVoice
```

### 3. Install dependencies

```bash
python -m venv venv
venv\Scripts\activate        # Windows  (use: source venv/bin/activate on macOS/Linux)
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy `.env.example` to `.env` and fill in the values:

```bash
copy .env.example .env       # Windows  (use: cp .env.example .env on macOS/Linux)
```

- `SECRET_KEY` — any long random string.
- `MAIL_USERNAME` / `MAIL_PASSWORD` — a Gmail address and a 16-character Gmail
  **App Password** (create one at https://myaccount.google.com/apppasswords).
- `ADMIN_EMAIL` / `ADMIN_PASSWORD` — the administrator account, created
  automatically the first time you run the app.

### 5. Run the application

```bash
python app.py
```

### 6. Open in your browser

```
http://127.0.0.1:5000
```

Students register at `/student/register`, verify via the emailed link, then log
in. Administrators log in at `/admin/login` with the credentials from `.env`.

---
## 👨‍💻 Developers

**Dhruvi Verma**

GitHub: https://github.com/dhruviverma226-alt

**Krishna Kanoje**

Github: https://github.com/krishnakanoje207-debug
---
