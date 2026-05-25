# HRMS — HR Management System

A simple, single-developer HR system built with Flask + PostgreSQL.

## Features
- Employee management (add, edit, remove, search)
- Attendance marking (present / absent / leave)
- Leave requests with admin approval
- Payroll generation with auto deduction
- Interview scheduling with Accept / Reject

## Setup

### 1. Create PostgreSQL database
```sql
CREATE DATABASE hrms_db;
```

### 2. Update DB URL in app.py
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://YOUR_USER:YOUR_PASSWORD@localhost/hrms_db'
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Initialize the database
Run the app then visit: http://localhost:5000/init-db
This creates all tables and an admin account.

### 5. Run the app
```bash
python app.py
```
Visit: http://localhost:5000

## Default Login
- **Username:** admin
- **Password:** admin123
- **Role:** Admin (full access)

## Roles
| Role     | Access |
|----------|--------|
| Admin    | Everything — employees, attendance, payroll, interviews, leaves |
| Employee | View own profile, apply leave, view own payslip |

## Project Structure
```
hrms/
├── app.py                  # All routes + models
├── requirements.txt
├── templates/
│   ├── base.html           # Sidebar layout
│   ├── login.html
│   ├── dashboard.html
│   ├── employees.html
│   ├── add_employee.html
│   ├── edit_employee.html
│   ├── attendance.html
│   ├── leaves.html
│   ├── apply_leave.html
│   ├── payroll.html
│   ├── interviews.html
│   └── add_interview.html
└── static/
    ├── css/style.css
    └── js/main.js
```
