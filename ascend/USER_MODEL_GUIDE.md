# User Model & Role-Based Authentication Guide

## 📋 Overview

The User model in ASCEND implements a complete authentication system with role-based access control. It handles three types of users: **Students**, **Mentors**, and **Admins**.

---

## 🗄️ User Model Structure

### Database Fields

```python
class User(UserMixin, db.Model):
    # Primary Key
    id = db.Column(db.Integer, primary_key=True)
    
    # Authentication Fields
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role Management
    role = db.Column(db.String(20), nullable=False, default='student', index=True)
    # Possible values: 'student', 'mentor', 'admin'
    
    # Profile Fields
    full_name = db.Column(db.String(100))
    bio = db.Column(db.Text)
    expertise = db.Column(db.String(255))  # For mentors
    
    # Approval/Verification
    is_verified = db.Column(db.Boolean, default=False, index=True)
    # Used to verify mentors before they can answer questions
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Field Explanations

| Field | Type | Purpose |
|-------|------|---------|
| `id` | Integer | Unique identifier (auto-incremented) |
| `username` | String(80) | Unique login name, indexed for fast lookup |
| `email` | String(120) | Unique email, indexed for fast lookup |
| `password_hash` | String(255) | **Never stores plain password!** Uses bcrypt hashing |
| `role` | String(20) | User type: 'student', 'mentor', or 'admin' |
| `full_name` | String(100) | Optional display name |
| `bio` | Text | User biography/description |
| `expertise` | String(255) | Comma-separated skills (for mentors) |
| `is_verified` | Boolean | Admin approval status (for mentors) |
| `created_at` | DateTime | Account creation timestamp |
| `updated_at` | DateTime | Last modification timestamp |

---

## 🔐 Password Hashing

### Why Hash Passwords?

**Never store plain text passwords!** If your database is compromised, attackers would have direct access to user passwords.

### How It Works

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Setting a password (during registration)
user = User(username='john', email='john@example.com')
user.set_password('my_secure_password')
# Stores: 'pbkdf2:sha256:260000$...' (hashed + salted)

# Checking a password (during login)
if user.check_password('entered_password'):
    login_user(user)  # Password correct!
else:
    return "Invalid password"  # Password wrong
```

### Implementation Details

**`set_password()` method:**
```python
def set_password(self, password):
    """Hash and store password using Werkzeug's security functions"""
    self.password_hash = generate_password_hash(password)
    # Uses PBKDF2 with SHA-256
    # Automatically adds a random salt
    # Makes rainbow table attacks impossible
```

**`check_password()` method:**
```python
def check_password(self, password):
    """Verify password against stored hash"""
    return check_password_hash(self.password_hash, password)
    # Returns True if password matches, False otherwise
```

### Security Features

1. **Salting**: Each password gets a unique random salt
2. **Key Stretching**: PBKDF2 with 260,000 iterations (slow = secure)
3. **One-Way**: Impossible to reverse the hash to get the original password
4. **Timing Attack Protection**: Constant-time comparison

---

## 👤 Flask-Login Integration

### UserMixin

The `User` model inherits from `UserMixin`, which provides:

```python
class User(UserMixin, db.Model):
    # UserMixin provides these methods automatically:
    
    # is_authenticated - Returns True if user is logged in
    # is_active - Returns True if account is active
    # is_anonymous - Returns False for regular users
    # get_id() - Returns the user ID as a string
```

### User Loader Function

In `app.py`, we define how Flask-Login loads users:

```python
@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login calls this function to reload the user object
    from the user ID stored in the session.
    """
    from models.user import User
    return User.query.get(int(user_id))
```

### How Sessions Work

1. **User logs in** → `login_user(user)` is called
2. **Session created** → User ID stored in encrypted session cookie
3. **Subsequent requests** → Flask-Login calls `load_user(user_id)`
4. **User object available** → Access via `current_user` in routes
5. **User logs out** → `logout_user()` clears the session

---

## 🎭 Role-Based Access Control (RBAC)

### The Three Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Student** | Ask questions, view roadmaps, rate mentors | Learning users |
| **Mentor** | Answer questions, view queue, earn trust score | Helping users |
| **Admin** | Verify mentors, moderate content, view analytics | Platform managers |

### Role Helper Methods

```python
# Check user role
if user.is_student():
    # Student-specific logic
    
if user.is_mentor():
    # Mentor-specific logic
    
if user.is_admin():
    # Admin-specific logic
```

**Implementation:**
```python
def is_student(self):
    """Check if user is a student"""
    return self.role == 'student'

def is_mentor(self):
    """Check if user is a mentor"""
    return self.role == 'mentor'

def is_admin(self):
    """Check if user is an admin"""
    return self.role == 'admin'
```

---

## 🛡️ Route Protection

### 1. Login Required

Protect routes that need authentication:

```python
from flask_login import login_required, current_user

@app.route('/profile')
@login_required  # Must be logged in
def profile():
    return jsonify(current_user.to_dict())
```

### 2. Role-Based Protection

Custom decorators for role-specific routes:

```python
def student_required(f):
    """Decorator to require student role"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_student():
            return jsonify({'error': 'Student access required'}), 403
        return f(*args, **kwargs)
    
    return decorated_function

# Usage
@student_bp.route('/questions')
@login_required
@student_required  # Must be a student
def get_questions():
    # Only students can access this
    questions = Question.query.filter_by(student_id=current_user.id).all()
    return jsonify([q.to_dict() for q in questions])
```

### 3. Mentor Verification

Additional check for verified mentors:

```python
@mentor_bp.route('/respond/<int:question_id>', methods=['POST'])
@login_required
@mentor_required
def respond_to_question(question_id):
    # Check if mentor is verified
    if not current_user.is_verified:
        return jsonify({'error': 'Mentor not verified yet'}), 403
    
    # Only verified mentors can respond
    # ... response logic
```

---

## 🔄 Complete Authentication Flow

### Registration

```python
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 1. Validate input
    if not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # 2. Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    # 3. Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        role=data.get('role', 'student')  # Default to student
    )
    
    # 4. Hash password (NEVER store plain text!)
    user.set_password(data['password'])
    
    # 5. Save to database
    db.session.add(user)
    db.session.commit()
    
    # 6. Create trust score for mentors
    if user.is_mentor():
        trust_score = TrustScore(mentor_id=user.id)
        db.session.add(trust_score)
        db.session.commit()
    
    return jsonify({'message': 'User registered', 'user': user.to_dict()}), 201
```

### Login

```python
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # 1. Find user by username or email
    user = User.query.filter(
        (User.username == data['username']) | (User.email == data['username'])
    ).first()
    
    # 2. Verify user exists
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # 3. Check password (uses check_password_hash internally)
    if not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # 4. Log in user (creates session)
    login_user(user, remember=data.get('remember', False))
    
    # 5. Return user data
    return jsonify({
        'message': 'Login successful',
        'user': user.to_dict(include_email=True)
    }), 200
```

### Accessing Current User

```python
from flask_login import current_user

@app.route('/dashboard')
@login_required
def dashboard():
    # current_user is automatically available
    if current_user.is_student():
        # Show student dashboard
        questions = current_user.questions.all()
        return jsonify({'questions': [q.to_dict() for q in questions]})
    
    elif current_user.is_mentor():
        # Show mentor dashboard
        responses = current_user.mentor_responses.all()
        return jsonify({'responses': [r.to_dict() for r in responses]})
    
    elif current_user.is_admin():
        # Show admin dashboard
        return jsonify({'message': 'Admin dashboard'})
```

---

## 🎯 Practical Examples

### Example 1: Create a Student

```python
# Create student user
student = User(
    username='john_student',
    email='john@example.com',
    role='student',
    full_name='John Doe'
)
student.set_password('secure_password_123')

db.session.add(student)
db.session.commit()

print(f"Created: {student}")  # <User john_student (student)>
```

### Example 2: Create a Mentor

```python
# Create mentor user
mentor = User(
    username='jane_mentor',
    email='jane@example.com',
    role='mentor',
    full_name='Jane Smith',
    bio='Experienced Python developer',
    expertise='Python, Machine Learning, Data Science'
)
mentor.set_password('mentor_password_456')

db.session.add(mentor)
db.session.commit()

# Create trust score for mentor
from models.trust_score import TrustScore
trust_score = TrustScore(mentor_id=mentor.id)
db.session.add(trust_score)
db.session.commit()

print(f"Mentor expertise: {mentor.get_expertise_list()}")
# ['Python', 'Machine Learning', 'Data Science']
```

### Example 3: Verify Login

```python
# User attempts to log in
username = 'john_student'
password = 'secure_password_123'

# Find user
user = User.query.filter_by(username=username).first()

if user and user.check_password(password):
    print("Login successful!")
    login_user(user)
else:
    print("Invalid credentials!")
```

### Example 4: Role-Based Logic

```python
# Different behavior based on role
user = User.query.get(1)

if user.is_student():
    # Students can ask questions
    question = Question(
        student_id=user.id,
        title="How do I learn Python?",
        description="I'm a beginner...",
        category="Python"
    )
    db.session.add(question)
    db.session.commit()

elif user.is_mentor():
    # Mentors can answer questions
    if user.is_verified:
        response = MentorResponse(
            question_id=1,
            mentor_id=user.id,
            response_text="Start with the basics..."
        )
        db.session.add(response)
        db.session.commit()
    else:
        print("Mentor not verified yet!")

elif user.is_admin():
    # Admins can verify mentors
    mentor = User.query.filter_by(role='mentor', id=2).first()
    mentor.is_verified = True
    db.session.commit()
    print(f"Verified mentor: {mentor.username}")
```

---

## 🔒 Security Best Practices

### ✅ DO:
- ✅ Always hash passwords with `set_password()`
- ✅ Use `@login_required` decorator for protected routes
- ✅ Check user roles before allowing actions
- ✅ Verify mentors before allowing them to answer
- ✅ Use HTTPS in production for secure cookies
- ✅ Set strong `SECRET_KEY` in production

### ❌ DON'T:
- ❌ Never store plain text passwords
- ❌ Don't expose password_hash in API responses
- ❌ Don't trust client-side role checks
- ❌ Don't skip verification for mentors
- ❌ Don't use weak passwords in production
- ❌ Don't share SECRET_KEY publicly

---

## 📊 Summary

The User model provides:

1. **Secure Authentication**: Password hashing with salt
2. **Session Management**: Flask-Login integration
3. **Role-Based Access**: Student, Mentor, Admin roles
4. **Verification System**: Admin approval for mentors
5. **Helper Methods**: Easy role checking
6. **Relationships**: Links to questions, responses, roadmaps, trust scores

This creates a robust, secure, and scalable authentication system for the ASCEND platform! 🚀
