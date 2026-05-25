from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import date, datetime
import secrets
import string
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'fallback-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hrms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── MODELS ───────────────────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='employee')
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emp_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    salary = db.Column(db.Float, default=0)
    joined_date = db.Column(db.Date, default=date.today)
    is_active = db.Column(db.Boolean, default=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='present')
    employee = db.relationship('Employee', backref='attendances')

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(300))
    status = db.Column(db.String(20), default='pending')
    applied_on = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship('Employee', backref='leaves')

class Payroll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    basic = db.Column(db.Float, default=0)
    deduction = db.Column(db.Float, default=0)
    net = db.Column(db.Float, default=0)
    generated_on = db.Column(db.DateTime, default=datetime.utcnow)
    employee = db.relationship('Employee', backref='payrolls')

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    scheduled_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.String(300))

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    subject = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(800), nullable=False)
    hr_reply = db.Column(db.String(800))
    status = db.Column(db.String(20), default='open')
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    replied_on = db.Column(db.DateTime)
    employee = db.relationship('Employee', backref='messages')

# ─── HELPERS ──────────────────────────────────────────────

def parse_date(s):
    """Convert date string from HTML form to Python date object."""
    if not s:
        return None
    return datetime.strptime(s, '%Y-%m-%d').date()

def generate_secure_password(length=14):
    """Create a strong password with uppercase, lowercase, digits, and symbols."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in "!@#$%^&*" for c in password)
        ):
            return password

def create_employee_user_account(employee):
    """Ensure the employee can log in with their employee number."""
    existing_user = User.query.filter_by(employee_id=employee.id).first()
    if existing_user:
        existing_user.username = employee.emp_number
        return existing_user, None

    plain_password = generate_secure_password()
    user = User(
        username=employee.emp_number,
        password=generate_password_hash(plain_password),
        role='employee',
        employee_id=employee.id
    )
    db.session.add(user)
    return user, plain_password

# ─── AUTH DECORATORS ──────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# ─── AUTH ROUTES ──────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User.query.join(Employee, User.employee_id == Employee.id).filter(
                User.role == 'employee',
                Employee.emp_number == username
            ).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['employee_id'] = user.employee_id
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── DASHBOARD ────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    today = date.today()
    if session.get('role') == 'admin':
        total_emp = Employee.query.filter_by(is_active=True).count()
        present_today = Attendance.query.filter_by(date=today, status='present').count()
        pending_leaves = Leave.query.filter_by(status='pending').count()
        pending_interviews = Interview.query.filter_by(status='pending').all()
        open_queries = Message.query.filter_by(status='open').count()
        recent_messages = Message.query.order_by(Message.created_on.desc()).limit(5).all()
        return render_template(
            'dashboard.html',
            dashboard_type='admin',
            total_emp=total_emp,
            present_today=present_today,
            pending_leaves=pending_leaves,
            interviews=pending_interviews,
            open_queries=open_queries,
            recent_messages=recent_messages
        )

    employee = Employee.query.get(session.get('employee_id')) if session.get('employee_id') else None
    today_attendance = None
    if employee:
        today_attendance = Attendance.query.filter_by(employee_id=employee.id, date=today).first()

    leave_records = Leave.query.filter_by(employee_id=session.get('employee_id')).order_by(Leave.applied_on.desc()).all()
    payroll_records = Payroll.query.filter_by(employee_id=session.get('employee_id')).order_by(
        Payroll.year.desc(),
        Payroll.month.desc()
    ).all()
    recent_messages = Message.query.filter_by(employee_id=session.get('employee_id')).order_by(
        Message.created_on.desc()
    ).limit(3).all()

    return render_template(
        'dashboard.html',
        dashboard_type='employee',
        employee=employee,
        attendance_status=today_attendance.status if today_attendance else 'not marked',
        leave_count=len(leave_records),
        pending_leave_count=sum(1 for leave in leave_records if leave.status == 'pending'),
        latest_payroll=payroll_records[0] if payroll_records else None,
        recent_messages=recent_messages
    )

# ─── EMPLOYEES ────────────────────────────────────────────

@app.route('/employees')
@login_required
@admin_required
def employees():
    search = request.args.get('q', '')
    dept = request.args.get('dept', '')
    query = Employee.query.filter_by(is_active=True)
    if search:
        query = query.filter(
            (Employee.first_name.ilike(f'%{search}%')) |
            (Employee.last_name.ilike(f'%{search}%')) |
            (Employee.emp_number.ilike(f'%{search}%'))
        )
    if dept:
        query = query.filter_by(department=dept)
    emps = query.all()
    departments = db.session.query(Employee.department).distinct().all()
    reset_info = session.pop('reset_password_info', None)
    return render_template(
        'employees.html',
        employees=emps,
        departments=departments,
        search=search,
        dept=dept,
        reset_info=reset_info
    )

@app.route('/employees/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_employee():
    if request.method == 'POST':
        emp = Employee(
            emp_number=request.form['emp_number'],
            first_name=request.form['first_name'],
            last_name=request.form['last_name'],
            position=request.form['position'],
            department=request.form['department'],
            email=request.form['email'],
            salary=float(request.form['salary'] or 0)
        )
        db.session.add(emp)
        db.session.commit()
        _, plain_password = create_employee_user_account(emp)
        db.session.commit()
        flash('Employee added successfully.', 'success')
        if plain_password:
            flash(f'Employee login created. Login ID: {emp.emp_number} | Temporary Password: {plain_password}', 'warning')
        return redirect(url_for('employees'))
    return render_template('add_employee.html')

@app.route('/employees/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_employee(id):
    emp = Employee.query.get_or_404(id)
    if request.method == 'POST':
        emp.emp_number = request.form['emp_number']
        emp.first_name = request.form['first_name']
        emp.last_name = request.form['last_name']
        emp.position = request.form['position']
        emp.department = request.form['department']
        emp.email = request.form['email']
        emp.salary = float(request.form['salary'] or 0)
        user = User.query.filter_by(employee_id=emp.id).first()
        if user:
            user.username = emp.emp_number
        db.session.commit()
        flash('Employee updated.', 'success')
        return redirect(url_for('employees'))
    return render_template('edit_employee.html', emp=emp)

@app.route('/employees/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    emp.is_active = False
    db.session.commit()
    flash('Employee removed.', 'success')
    return redirect(url_for('employees'))

@app.route('/employees/reset-password/<int:id>', methods=['POST'])
@login_required
@admin_required
def reset_employee_password(id):
    employee = Employee.query.get_or_404(id)
    user = User.query.filter_by(employee_id=employee.id).first()
    if not user:
        user, _ = create_employee_user_account(employee)
    new_password = generate_secure_password()
    user.username = employee.emp_number
    user.password = generate_password_hash(new_password)
    db.session.commit()
    session['reset_password_info'] = {
        'name': f'{employee.first_name} {employee.last_name}',
        'login_id': employee.emp_number,
        'password': new_password
    }
    flash(
        f'Password reset for {employee.first_name} {employee.last_name}. Login ID: {employee.emp_number} | New Temporary Password: {new_password}',
        'warning'
    )
    return redirect(url_for('employees'))

# ─── ATTENDANCE ───────────────────────────────────────────

@app.route('/attendance', methods=['GET', 'POST'])
@login_required
@admin_required
def attendance():
    today = date.today()
    employees = Employee.query.filter_by(is_active=True).all()
    if request.method == 'POST':
        mark_date = parse_date(request.form.get('mark_date', str(today)))
        for emp in employees:
            status = request.form.get(f'status_{emp.id}', 'absent')
            existing = Attendance.query.filter_by(employee_id=emp.id, date=mark_date).first()
            if existing:
                existing.status = status
            else:
                db.session.add(Attendance(employee_id=emp.id, date=mark_date, status=status))
        db.session.commit()
        flash('Attendance saved.', 'success')
        return redirect(url_for('attendance'))
    records = {a.employee_id: a.status for a in Attendance.query.filter_by(date=today).all()}
    return render_template('attendance.html', employees=employees, records=records, today=today)

# ─── LEAVE ────────────────────────────────────────────────

@app.route('/leaves')
@login_required
def leaves():
    if session['role'] == 'admin':
        all_leaves = Leave.query.order_by(Leave.applied_on.desc()).all()
    else:
        all_leaves = Leave.query.filter_by(employee_id=session['employee_id']).order_by(Leave.applied_on.desc()).all()
    return render_template('leaves.html', leaves=all_leaves)

@app.route('/leaves/apply', methods=['GET', 'POST'])
@login_required
def apply_leave():
    if request.method == 'POST':
        leave = Leave(
            employee_id=session['employee_id'],
            start_date=parse_date(request.form['start_date']),
            end_date=parse_date(request.form['end_date']),
            reason=request.form['reason']
        )
        db.session.add(leave)
        db.session.commit()
        flash('Leave application submitted.', 'success')
        return redirect(url_for('leaves'))
    return render_template('apply_leave.html')

@app.route('/leaves/action/<int:id>/<action>')
@login_required
@admin_required
def leave_action(id, action):
    leave = Leave.query.get_or_404(id)
    if action in ['approved', 'rejected']:
        leave.status = action
        db.session.commit()
        flash(f'Leave {action}.', 'success')
    return redirect(url_for('leaves'))

@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    if request.method == 'POST':
        if session.get('role') != 'employee' or not session.get('employee_id'):
            flash('Only employees can send queries here.', 'danger')
            return redirect(url_for('messages'))

        subject = request.form['subject'].strip()
        body = request.form['message'].strip()
        if not subject or not body:
            flash('Subject and message are required.', 'danger')
            return redirect(url_for('messages'))

        query = Message(employee_id=session['employee_id'], subject=subject, message=body)
        db.session.add(query)
        db.session.commit()
        flash('Your query has been sent to HR.', 'success')
        return redirect(url_for('messages'))

    if session.get('role') == 'admin':
        message_records = Message.query.order_by(Message.status.asc(), Message.created_on.desc()).all()
    else:
        message_records = Message.query.filter_by(employee_id=session.get('employee_id')).order_by(
            Message.created_on.desc()
        ).all()
    return render_template('messages.html', messages=message_records)

@app.route('/messages/reply/<int:id>', methods=['POST'])
@login_required
@admin_required
def reply_message(id):
    query = Message.query.get_or_404(id)
    reply = request.form['reply'].strip()
    if not reply:
        flash('Reply cannot be empty.', 'danger')
        return redirect(url_for('messages'))
    query.hr_reply = reply
    query.status = 'resolved'
    query.replied_on = datetime.utcnow()
    db.session.commit()
    flash('Reply sent to employee.', 'success')
    return redirect(url_for('messages'))

# ─── PAYROLL ──────────────────────────────────────────────

@app.route('/payroll')
@login_required
@admin_required
def payroll():
    employees = Employee.query.filter_by(is_active=True).all()
    records = Payroll.query.order_by(Payroll.year.desc(), Payroll.month.desc()).all()
    return render_template('payroll.html', employees=employees, records=records)

@app.route('/payroll/generate', methods=['POST'])
@login_required
@admin_required
def generate_payroll():
    emp_id = int(request.form['employee_id'])
    month = int(request.form['month'])
    year = int(request.form['year'])
    emp = Employee.query.get_or_404(emp_id)
    existing = Payroll.query.filter_by(employee_id=emp_id, month=month, year=year).first()
    if existing:
        flash('Payroll already generated for this month.', 'warning')
        return redirect(url_for('payroll'))
    basic = emp.salary
    deduction = round(basic * 0.12, 2)
    net = round(basic - deduction, 2)
    p = Payroll(employee_id=emp_id, month=month, year=year, basic=basic, deduction=deduction, net=net)
    db.session.add(p)
    db.session.commit()
    flash('Payroll generated.', 'success')
    return redirect(url_for('payroll'))

# ─── INTERVIEWS ───────────────────────────────────────────

@app.route('/interviews')
@login_required
@admin_required
def interviews():
    all_interviews = Interview.query.order_by(Interview.scheduled_date.desc()).all()
    return render_template('interviews.html', interviews=all_interviews)

@app.route('/interviews/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_interview():
    if request.method == 'POST':
        iv = Interview(
            candidate_name=request.form['candidate_name'],
            position=request.form['position'],
            department=request.form['department'],
            scheduled_date=parse_date(request.form.get('scheduled_date')),
            notes=request.form.get('notes', '')
        )
        db.session.add(iv)
        db.session.commit()
        flash('Interview scheduled.', 'success')
        return redirect(url_for('interviews'))
    return render_template('add_interview.html')

@app.route('/interviews/action/<int:id>/<action>')
@login_required
@admin_required
def interview_action(id, action):
    iv = Interview.query.get_or_404(id)
    if action in ['accepted', 'rejected']:
        iv.status = action
        db.session.commit()
        flash(f'Candidate {action}.', 'success')
    return redirect(url_for('interviews'))

# ─── INIT ─────────────────────────────────────────────────

@app.route('/init-db')
def init_db():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('admin123'), role='admin')
        db.session.add(admin)
        db.session.commit()
    return 'DB initialized. Admin: admin / admin123'

@app.route('/create-employee-user')
def create_employee_user():
    emp = Employee.query.first()
    if not emp:
        return 'No employees found. Add an employee from admin panel first, then visit this URL.'
    if not User.query.filter_by(username='employee1').first():
        user = User(
            username='employee1',
            password=generate_password_hash('emp123'),
            role='employee',
            employee_id=emp.id
        )
        db.session.add(user)
        db.session.commit()
        return f'Done! Login: employee1 / emp123 — linked to {emp.first_name} {emp.last_name}'
    return 'User employee1 already exists. Login: employee1 / emp123'

if __name__ == '__main__':
    app.run(debug=True)
