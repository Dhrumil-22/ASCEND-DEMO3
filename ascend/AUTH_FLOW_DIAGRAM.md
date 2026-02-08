# Role-Based Authentication Flow Diagram

## 🔄 Complete Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER REGISTRATION FLOW                        │
└─────────────────────────────────────────────────────────────────┘

1. User submits registration form
   ↓
2. Validate input (username, email, password)
   ↓
3. Check if username/email already exists
   ↓
4. Create User object with role (student/mentor/admin)
   ↓
5. Hash password using set_password()
   │  → generate_password_hash('plain_password')
   │  → Stores: 'pbkdf2:sha256:260000$salt$hash'
   ↓
6. Save user to database
   ↓
7. If mentor: Create TrustScore (is_verified=False)
   ↓
8. Return success response


┌─────────────────────────────────────────────────────────────────┐
│                      USER LOGIN FLOW                             │
└─────────────────────────────────────────────────────────────────┘

1. User submits login credentials
   ↓
2. Find user by username or email
   ↓
3. Verify password using check_password()
   │  → check_password_hash(stored_hash, entered_password)
   │  → Returns True/False
   ↓
4. If password correct:
   │  → login_user(user) creates session
   │  → Session cookie sent to browser
   │  → User ID stored in encrypted cookie
   ↓
5. Return user data (without password_hash!)


┌─────────────────────────────────────────────────────────────────┐
│                  AUTHENTICATED REQUEST FLOW                      │
└─────────────────────────────────────────────────────────────────┘

1. User makes request with session cookie
   ↓
2. Flask-Login reads session cookie
   ↓
3. Calls user_loader function with user_id
   │  → User.query.get(user_id)
   ↓
4. Loads User object into current_user
   ↓
5. @login_required decorator checks if authenticated
   ↓
6. Role decorator checks user.role
   │  → @student_required → user.is_student()
   │  → @mentor_required → user.is_mentor()
   │  → @admin_required → user.is_admin()
   ↓
7. If authorized: Execute route function
   │  If not: Return 403 Forbidden
```

## 🎭 Role-Based Access Control

```
┌──────────────────────────────────────────────────────────────────┐
│                         USER ROLES                                │
└──────────────────────────────────────────────────────────────────┘

STUDENT (role='student')
├── Can ask questions
├── Can view roadmaps
├── Can rate mentor responses
├── Can view recommended mentors
└── Cannot answer questions

MENTOR (role='mentor')
├── Can answer questions (if is_verified=True)
├── Can view question queue
├── Can earn trust score
├── Can update expertise
└── Cannot ask questions (in current design)

ADMIN (role='admin')
├── Can verify mentors (set is_verified=True)
├── Can view all users
├── Can moderate content
├── Can view analytics
├── Can delete users
└── Full platform access


┌──────────────────────────────────────────────────────────────────┐
│                    ROUTE PROTECTION LAYERS                        │
└──────────────────────────────────────────────────────────────────┘

Layer 1: @login_required
         ↓
         Checks if user is authenticated
         If not → Redirect to login (401)

Layer 2: @role_required (student/mentor/admin)
         ↓
         Checks if user.role matches required role
         If not → Return 403 Forbidden

Layer 3: Additional checks (e.g., is_verified)
         ↓
         Custom logic for specific requirements
         If not → Return 403 Forbidden

Layer 4: Route logic executes
         ↓
         User has full access to the endpoint
```

## 🔐 Password Security

```
┌──────────────────────────────────────────────────────────────────┐
│                    PASSWORD HASHING PROCESS                       │
└──────────────────────────────────────────────────────────────────┘

Plain Password: "mySecurePassword123"
                ↓
        generate_password_hash()
                ↓
        ┌───────────────────┐
        │  1. Generate Salt │  (Random: "a8f3d2e1")
        └───────────────────┘
                ↓
        ┌───────────────────┐
        │  2. Combine       │  (Password + Salt)
        └───────────────────┘
                ↓
        ┌───────────────────┐
        │  3. Hash (PBKDF2) │  (260,000 iterations)
        └───────────────────┘
                ↓
Stored Hash: "pbkdf2:sha256:260000$a8f3d2e1$9f8e7d6c5b4a..."

Benefits:
✓ Same password → Different hash (due to random salt)
✓ Cannot reverse hash to get password
✓ Slow hashing prevents brute force attacks
✓ Salt prevents rainbow table attacks


┌──────────────────────────────────────────────────────────────────┐
│                   PASSWORD VERIFICATION                           │
└──────────────────────────────────────────────────────────────────┘

User enters: "mySecurePassword123"
                ↓
        check_password_hash(stored_hash, entered_password)
                ↓
        ┌───────────────────┐
        │  1. Extract Salt  │  (From stored hash)
        └───────────────────┘
                ↓
        ┌───────────────────┐
        │  2. Hash Input    │  (Same algorithm + salt)
        └───────────────────┘
                ↓
        ┌───────────────────┐
        │  3. Compare       │  (Constant-time comparison)
        └───────────────────┘
                ↓
        Returns: True/False
```

## 📊 Database Relationships

```
┌──────────────────────────────────────────────────────────────────┐
│                    USER MODEL RELATIONSHIPS                       │
└──────────────────────────────────────────────────────────────────┘

                        ┌─────────┐
                        │  USER   │
                        │ (Model) │
                        └────┬────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐         ┌──────────┐        ┌──────────┐
   │Question │         │ Roadmap  │        │MentorResp│
   │(Student)│         │(Student) │        │ (Mentor) │
   └─────────┘         └──────────┘        └──────────┘
                                                  │
                                                  ▼
                                           ┌──────────┐
                                           │TrustScore│
                                           │ (Mentor) │
                                           └──────────┘

Student User:
├── questions (one-to-many)
└── roadmaps (one-to-many)

Mentor User:
├── mentor_responses (one-to-many)
└── trust_score (one-to-one)

Admin User:
└── No direct relationships (manages all)
```

## 🛡️ Security Checklist

```
┌──────────────────────────────────────────────────────────────────┐
│                      SECURITY MEASURES                            │
└──────────────────────────────────────────────────────────────────┘

✅ Password Security
   ├── Passwords hashed with PBKDF2-SHA256
   ├── Random salt for each password
   ├── 260,000 iterations (slow = secure)
   └── Never store plain text passwords

✅ Session Security
   ├── Encrypted session cookies
   ├── HttpOnly cookies (prevent XSS)
   ├── SameSite cookies (prevent CSRF)
   └── Secure cookies in production (HTTPS only)

✅ Access Control
   ├── @login_required for authentication
   ├── Role-based decorators for authorization
   ├── Server-side role verification
   └── is_verified check for mentors

✅ Database Security
   ├── Indexed fields for fast lookups
   ├── Unique constraints on username/email
   ├── Cascade delete for data integrity
   └── Timestamps for audit trail

✅ API Security
   ├── Never expose password_hash
   ├── Validate all input data
   ├── Use HTTPS in production
   └── Rate limiting (recommended)
```

---

## 📝 Quick Reference

### Creating Users

```python
# Student
student = User(username='john', email='john@ex.com', role='student')
student.set_password('pass123')

# Mentor
mentor = User(username='jane', email='jane@ex.com', role='mentor')
mentor.set_password('pass456')
mentor.expertise = 'Python, ML'

# Admin
admin = User(username='admin', email='admin@ex.com', role='admin')
admin.set_password('admin789')
```

### Checking Roles

```python
if current_user.is_student():
    # Student logic
    
if current_user.is_mentor() and current_user.is_verified:
    # Verified mentor logic
    
if current_user.is_admin():
    # Admin logic
```

### Protecting Routes

```python
@app.route('/student/dashboard')
@login_required
@student_required
def student_dashboard():
    # Only authenticated students can access
    pass

@app.route('/mentor/queue')
@login_required
@mentor_required
def mentor_queue():
    # Only authenticated mentors can access
    if not current_user.is_verified:
        return jsonify({'error': 'Not verified'}), 403
    pass

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    # Only authenticated admins can access
    pass
```

This comprehensive authentication system ensures secure, role-based access control throughout the ASCEND platform! 🔒
