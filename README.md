HR Management System
A Full-Stack Web Application for Digital HR Operations
Internship Project  |  Edutainer  |  Feb 2026 – May 2026

Python	Flask	SQLite	SQLAlchemy	HTML5 / CSS3	JavaScript	Jinja2

Werkzeug	MVC Architecture	Role-Based Auth	PBKDF2-SHA256	Render (Deployed)

🔗  View Source Code on GitHub     🚀  Live Demo on Render

Project Overview
The HR Management System (HRMS) is a secure, full-stack web application built to fully digitalize routine human resource operations that are traditionally handled through paper registers or Excel sheets. The system provides a clean, role-based interface for HR Managers (Admins) and Employees, eliminating manual processes and improving organizational efficiency.

Project Type	Full-Stack Web Application (Internship Project)
Organization	Edutainer
Duration	February 2026 – May 2026
Architecture	MVC (Model-View-Controller)
Deployment	Render (Cloud Platform)
Database	SQLite with SQLAlchemy ORM (zero-installation)

Technology Stack

⚙️  Backend	🎨  Frontend
Python	HTML5 & CSS3
Flask	JavaScript (Vanilla)
SQLAlchemy ORM	Jinja2 Templating Engine
SQLite	Template Inheritance
Werkzeug (password hashing)	12 Responsive Pages
Flask Sessions	Custom Python Decorators

Features & Functionality

👤  Admin Portal (HR Manager)
•Add, edit, and remove employee records
•Mark daily attendance for all employees
•Generate and view monthly payslips
•Approve or reject employee leave requests
•Schedule candidate interviews with Accept / Reject decision tracking
•Full visibility and control across all employee data

💼  Employee Self-Service Portal
•Personalized dashboard showing only the logged-in employee’s data
•View personal attendance summary
•Apply for leave and track request status in real time
•Check monthly payslip with detailed salary breakdown
•Zero access to any other employee’s information

🔒  Security & Access Control
•Werkzeug PBKDF2-SHA256 password hashing — passwords never stored as plain text
•Flask sessions store authenticated user role and employee ID
•All sensitive routes protected with custom Python decorators
◦@login_required — blocks unauthenticated access
◦@admin_required — restricts admin-only routes from employee access

Application Architecture

The application follows the MVC (Model-View-Controller) pattern:

🏗️  Layer	📝  Responsibility
Model	SQLAlchemy ORM models define database schema and relationships in pure Python — no raw SQL
View	Jinja2 templates with inheritance from a single base layout shared across all 12 pages
Controller	Flask routes handle HTTP requests, form processing, session management, and business logic

Payroll Calculation
Payroll is fully automated and compliant with Indian labor law. Net salary is calculated using:

Net Salary = Gross Salary - EPF Deduction
EPF Deduction = Gross Salary × 12%

(As per the Government of India’s Employee Provident Fund Act)

The system uses upsert logic to prevent duplicate payroll records for the same employee in the same month.

Technical Challenges Solved

1. SQLite Date Type Error
SQLite does not natively enforce date types, causing inconsistent data handling across queries. This was resolved by writing a reusable parse_date() helper function following the DRY (Don’t Repeat Yourself) principle, applied uniformly across all date fields in the application.

2. Duplicate Records Prevention
Attendance and payroll modules required upsert logic (insert-or-update) to prevent creating duplicate entries for the same employee on the same date or month. This was implemented using SQLAlchemy’s query-based conditional writes.

3. Completely Separate Dashboards
Admin and Employee users see entirely different interfaces after login. This was achieved using session-based role checking — the authenticated role is stored in the Flask session and read on every protected route to decide what data is fetched and which template is rendered.

4. Database Migration (PostgreSQL → SQLite)
The project was migrated from PostgreSQL to SQLite for zero-installation portability — any developer can clone the repo and run it without setting up a database server. Thanks to SQLAlchemy ORM abstraction, this migration required only a single configuration line change.

Database Design
The database is managed entirely through SQLAlchemy ORM. All tables are defined as Python classes — SQLAlchemy automatically translates them into SQL schema. The core models include:

📄  Model	📋  Description
Employee	Stores employee profile, role, and hashed credentials
Attendance	Daily attendance records per employee (present/absent)
Leave Request	Employee leave applications with admin approval status
Payroll	Monthly payslip records with gross, EPF, and net salary
Interview	Candidate interview records with scheduling and decision status

Project Structure

HRMS/
├── app.py                  # Flask app factory, route definitions
├── models.py               # SQLAlchemy ORM models
├── decorators.py           # @login_required, @admin_required
├── helpers.py              # parse_date() and utility functions
├── templates/
│   ├── base.html           # Base layout (shared across 12 pages)
│   ├── admin/              # Admin dashboard templates
│   └── employee/           # Employee self-service templates
├── static/
│   ├── css/                # Stylesheets
│   └── js/                 # JavaScript files
└── requirements.txt        # Python dependencies

Local Setup & Installation

Prerequisites
•Python 3.8 or higher
•pip (Python package installer)
•Git

Steps

# 1. Clone the repository
git clone https://github.com/NithinGowda02/HRMS.git
cd HRMS

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py

# The app will be available at: http://localhost:5000

Deployment
The application is deployed on Render (https://render.com), a cloud platform that supports Python web services. Render automatically detects the Flask application and serves it via Gunicorn.

Platform	Render
Live URL	https://hrms-3r20.onrender.com/
Web Server	Gunicorn (WSGI)
Database	SQLite (file-based, zero configuration)
Env Variables	SECRET_KEY stored as Render environment variable

Key Learnings
•Built a complete full-stack web application from scratch using Flask and SQLAlchemy
•Implemented role-based access control using custom Python decorators and session management
•Applied the MVC design pattern to keep code modular, maintainable, and scalable
•Used Jinja2 template inheritance to maintain a consistent UI across all 12 pages
•Practiced the DRY principle by extracting reusable helper functions
•Understood ORM abstraction — how SQLAlchemy converts Python classes to SQL without writing raw queries
•Gained experience with upsert logic to maintain data integrity
•Learned to migrate between database backends with minimal code changes thanks to ORM
•Deployed a production Flask application on a cloud platform (Render)

HR Management System
Built with Python • Flask • SQLAlchemy • SQLite
GitHub Repository   •   Live Demo
