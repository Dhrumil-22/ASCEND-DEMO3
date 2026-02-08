# Authentication System Guide - ASCEND Flask Backend

## 📋 Overview

The ASCEND authentication system provides secure user registration, login, and session management with role-based access control. It implements industry-standard security practices including password hashing, session-based authentication, and input validation.

---

## 🔐 Authentication Routes

### Base URL: `/auth`

All authentication routes are prefixed with `/auth`:

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | ❌ No |
| POST | `/auth/login` | Login user | ❌ No |
| POST | `/auth/logout` | Logout user | ✅ Yes |
| GET | `/auth/profile` | Get user profile | ✅ Yes |
| PUT | `/auth/profile` | Update profile | ✅ Yes |
| POST | `/auth/change-password` | Change password | ✅ Yes |

---

## 1️⃣ POST /auth/register - User Registration

### Purpose
Register a new user account (student or mentor). Admin accounts cannot be created via this endpoint.

### Request

**URL:** `POST http://localhost:5000/auth/register`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "username": "john_student",
  "email": "john@example.com",
  "password": "secure_password_123",
  "role": "student",
  "full_name": "John Doe"
}
```

**Required Fields:**
- `username` (string): Unique username (3-80 characters)
- `email` (string): Valid email address (unique)
- `password` (string): Password (will be hashed)

**Optional Fields:**
- `role` (string): Either `"student"` or `"mentor"` (default: `"student"`)
- `full_name` (string): User's full name

### Response

**Success (201 Created):**

**For Students:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "john_student",
    "role": "student",
    "full_name": "John Doe",
    "bio": null,
    "expertise": [],
    "is_verified": false,
    "created_at": "2026-02-05T12:00:00"
  }
}
```

**For Mentors:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 2,
    "username": "jane_mentor",
    "role": "mentor",
    "full_name": "Jane Smith",
    "bio": null,
    "expertise": [],
    "is_verified": false,
    "created_at": "2026-02-05T12:00:00"
  },
  "note": "Your mentor account requires admin approval before you can answer questions"
}
```

**Error Responses:**

**400 Bad Request - Missing Fields:**
```json
{
  "error": "Username, email, and password are required"
}
```

**400 Bad Request - Username Exists:**
```json
{
  "error": "Username already exists"
}
```

**400 Bad Request - Email Exists:**
```json
{
  "error": "Email already registered"
}
```

**400 Bad Request - Invalid Role:**
```json
{
  "error": "Invalid role. Must be \"student\" or \"mentor\""
}
```

**403 Forbidden - Admin Registration Attempt:**
```json
{
  "error": "Admin accounts cannot be created via registration",
  "message": "Admin accounts must be created manually by system administrators"
}
```

### Registration Rules

1. **Students:**
   - Register normally
   - Get immediate access to all student features
   - Can ask questions, view roadmaps, rate mentors

2. **Mentors:**
   - Register with `is_verified = False`
   - Cannot answer questions until admin approves
   - Automatically get a TrustScore initialized to 50
   - Need admin verification to become active

3. **Admins:**
   - **Cannot** register via API
   - Must be created manually by system administrators
   - Created directly in database or via admin script

### What Happens During Registration?

```
1. Validate input (username, email, password)
   ↓
2. Check role (prevent admin creation)
   ↓
3. Check if username/email already exists
   ↓
4. Create User object
   ↓
5. Hash password using set_password()
   ↓
6. Set is_verified = False for mentors
   ↓
7. Save user to database
   ↓
8. If mentor: Create TrustScore (initial score = 50)
   ↓
9. Return user data (without password_hash!)
```

---

## 2️⃣ POST /auth/login - User Login

### Purpose
Authenticate a user and create a session.

### Request

**URL:** `POST http://localhost:5000/auth/login`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "username": "john_student",
  "password": "secure_password_123",
  "remember": true
}
```

**Required Fields:**
- `username` (string): Username or email address
- `password` (string): User's password

**Optional Fields:**
- `remember` (boolean): Remember user session (default: `false`)
  - `true`: Session lasts 7 days
  - `false`: Session expires when browser closes

### Response

**Success (200 OK):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "john_student",
    "email": "john@example.com",
    "role": "student",
    "full_name": "John Doe",
    "bio": null,
    "expertise": [],
    "is_verified": false,
    "created_at": "2026-02-05T12:00:00"
  }
}
```

**Note:** Session cookie is automatically set in response headers.

**Error Responses:**

**400 Bad Request - Missing Fields:**
```json
{
  "error": "Username and password are required"
}
```

**401 Unauthorized - Invalid Credentials:**
```json
{
  "error": "Invalid username or password"
}
```

### What Happens During Login?

```
1. Validate input (username, password)
   ↓
2. Find user by username OR email
   ↓
3. Check if user exists
   ↓
4. Verify password using check_password()
   ↓
5. If valid: Create session with login_user()
   ↓
6. Set session cookie (encrypted)
   ↓
7. Return user data
```

### Session Management

**Session Cookie:**
- Name: `session`
- Encrypted: Yes
- HttpOnly: Yes (prevents XSS attacks)
- SameSite: Lax (prevents CSRF attacks)
- Secure: Yes (in production, HTTPS only)
- Duration: 
  - Default: Browser session (closes when browser closes)
  - Remember me: 7 days

**Session Storage:**
- User ID stored in encrypted cookie
- Flask-Login manages session lifecycle
- Automatic user loading on each request

---

## 3️⃣ POST /auth/logout - User Logout

### Purpose
End the current user's session.

### Request

**URL:** `POST http://localhost:5000/auth/logout`

**Headers:**
```
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Body:** None required

**Authentication:** Required (must be logged in)

### Response

**Success (200 OK):**
```json
{
  "message": "Logout successful"
}
```

**Error Responses:**

**401 Unauthorized - Not Logged In:**
```json
{
  "error": "Unauthorized",
  "message": "Authentication required"
}
```

### What Happens During Logout?

```
1. Check if user is authenticated
   ↓
2. Call logout_user() from Flask-Login
   ↓
3. Clear session cookie
   ↓
4. Remove user from current_user
   ↓
5. Return success message
```

---

## 🔄 Complete Authentication Flow

### Registration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    REGISTRATION FLOW                         │
└─────────────────────────────────────────────────────────────┘

Client                          Server                    Database
  │                               │                           │
  │  POST /auth/register          │                           │
  │  {username, email, password}  │                           │
  ├──────────────────────────────>│                           │
  │                               │                           │
  │                               │ Validate input            │
  │                               │ Check role != 'admin'     │
  │                               │                           │
  │                               │ Query: Check username     │
  │                               ├──────────────────────────>│
  │                               │<──────────────────────────┤
  │                               │ Result: Not exists        │
  │                               │                           │
  │                               │ Query: Check email        │
  │                               ├──────────────────────────>│
  │                               │<──────────────────────────┤
  │                               │ Result: Not exists        │
  │                               │                           │
  │                               │ Create User object        │
  │                               │ Hash password             │
  │                               │ Set is_verified = False   │
  │                               │   (for mentors)           │
  │                               │                           │
  │                               │ INSERT INTO users         │
  │                               ├──────────────────────────>│
  │                               │<──────────────────────────┤
  │                               │ User created (ID: 1)      │
  │                               │                           │
  │                               │ If mentor:                │
  │                               │ INSERT INTO trust_scores  │
  │                               ├──────────────────────────>│
  │                               │<──────────────────────────┤
  │                               │ TrustScore created        │
  │                               │                           │
  │  201 Created                  │                           │
  │  {message, user, note}        │                           │
  │<──────────────────────────────┤                           │
  │                               │                           │
```

### Login Flow

```
┌─────────────────────────────────────────────────────────────┐
│                       LOGIN FLOW                             │
└─────────────────────────────────────────────────────────────┘

Client                          Server                    Database
  │                               │                           │
  │  POST /auth/login             │                           │
  │  {username, password}         │                           │
  ├──────────────────────────────>│                           │
  │                               │                           │
  │                               │ Validate input            │
  │                               │                           │
  │                               │ Query: Find user          │
  │                               │ WHERE username OR email   │
  │                               ├──────────────────────────>│
  │                               │<──────────────────────────┤
  │                               │ Result: User object       │
  │                               │                           │
  │                               │ Check password:           │
  │                               │ check_password_hash()     │
  │                               │                           │
  │                               │ If valid:                 │
  │                               │   login_user()            │
  │                               │   Create session          │
  │                               │   Generate cookie         │
  │                               │                           │
  │  200 OK                       │                           │
  │  Set-Cookie: session=xyz      │                           │
  │  {message, user}              │                           │
  │<──────────────────────────────┤                           │
  │                               │                           │
  │  Store cookie                 │                           │
  │                               │                           │
```

### Authenticated Request Flow

```
┌─────────────────────────────────────────────────────────────┐
│                  AUTHENTICATED REQUEST                       │
└─────────────────────────────────────────────────────────────┘

Client                          Server                    Database
  │                               │                           │
  │  GET /student/questions       │                           │
  │  Cookie: session=xyz          │                           │
  ├──────────────────────────────>│                           │
  │                               │                           │
  │                               │ Read session cookie       │
  │                               │ Decrypt user_id           │
  │                               │                           │
  │                               │ Call user_loader()        │
  │                               │ Query: Get user by ID     │
  │                               ├──────────────────────────>│
  │                               │<──────────────────────────┤
  │                               │ Result: User object       │
  │                               │                           │
  │                               │ Set current_user          │
  │                               │                           │
  │                               │ Check @login_required     │
  │                               │ ✓ User authenticated      │
  │                               │                           │
  │                               │ Check @student_required   │
  │                               │ ✓ User is student         │
  │                               │                           │
  │                               │ Execute route logic       │
  │                               │ Query: Get questions      │
  │                               ├──────────────────────────>│
  │                               │<──────────────────────────┤
  │                               │ Result: Questions         │
  │                               │                           │
  │  200 OK                       │                           │
  │  {questions: [...]}           │                           │
  │<──────────────────────────────┤                           │
  │                               │                           │
```

---

## 🔒 Security Features

### 1. Password Security

**Hashing Algorithm:** PBKDF2-SHA256
- **Iterations:** 260,000 (slow = secure)
- **Salt:** Random, unique per password
- **Length:** 255 characters

**Example:**
```
Plain password: "mySecurePassword123"
Stored hash: "pbkdf2:sha256:260000$a8f3d2e1$9f8e7d6c5b4a3e2f1..."
```

**Benefits:**
- ✅ Cannot reverse hash to get password
- ✅ Same password → Different hash (random salt)
- ✅ Slow hashing prevents brute force
- ✅ Resistant to rainbow table attacks

### 2. Session Security

**Cookie Settings:**
```python
SESSION_COOKIE_HTTPONLY = True   # Prevents XSS attacks
SESSION_COOKIE_SAMESITE = 'Lax'  # Prevents CSRF attacks
SESSION_COOKIE_SECURE = True     # HTTPS only (production)
PERMANENT_SESSION_LIFETIME = 7 days
```

**Session Flow:**
1. User logs in → Session created
2. Session ID stored in encrypted cookie
3. Cookie sent with every request
4. Server validates and loads user
5. User logs out → Session destroyed

### 3. Input Validation

**Registration Validation:**
- ✅ Required fields check
- ✅ Email format validation
- ✅ Username uniqueness
- ✅ Email uniqueness
- ✅ Role validation (student/mentor only)
- ✅ Admin creation prevention

**Login Validation:**
- ✅ Required fields check
- ✅ User existence check
- ✅ Password verification
- ✅ Timing attack protection

### 4. Role-Based Access

**Access Levels:**
```
Public Routes (No auth):
  - POST /auth/register
  - POST /auth/login

Authenticated Routes (Login required):
  - POST /auth/logout
  - GET /auth/profile
  - PUT /auth/profile
  - POST /auth/change-password

Role-Specific Routes:
  - /student/* → Students only
  - /mentor/* → Mentors only (+ verified check)
  - /admin/* → Admins only
```

---

## 📝 Testing the Authentication System

### Test 1: Register a Student

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice_student",
    "email": "alice@example.com",
    "password": "student_pass_123",
    "role": "student",
    "full_name": "Alice Johnson"
  }'
```

**Expected Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "username": "alice_student",
    "role": "student",
    ...
  }
}
```

### Test 2: Register a Mentor

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bob_mentor",
    "email": "bob@example.com",
    "password": "mentor_pass_456",
    "role": "mentor",
    "full_name": "Bob Smith"
  }'
```

**Expected Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 2,
    "username": "bob_mentor",
    "role": "mentor",
    "is_verified": false,
    ...
  },
  "note": "Your mentor account requires admin approval before you can answer questions"
}
```

### Test 3: Try to Register Admin (Should Fail)

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin_user",
    "email": "admin@example.com",
    "password": "admin_pass_789",
    "role": "admin"
  }'
```

**Expected Response (403):**
```json
{
  "error": "Admin accounts cannot be created via registration",
  "message": "Admin accounts must be created manually by system administrators"
}
```

### Test 4: Login

```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "username": "alice_student",
    "password": "student_pass_123",
    "remember": true
  }'
```

**Expected Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "alice_student",
    "email": "alice@example.com",
    ...
  }
}
```

**Note:** Session cookie saved to `cookies.txt`

### Test 5: Access Protected Route

```bash
curl -X GET http://localhost:5000/auth/profile \
  -H "Content-Type: application/json" \
  -b cookies.txt
```

**Expected Response (200):**
```json
{
  "user": {
    "id": 1,
    "username": "alice_student",
    ...
  }
}
```

### Test 6: Logout

```bash
curl -X POST http://localhost:5000/auth/logout \
  -H "Content-Type: application/json" \
  -b cookies.txt
```

**Expected Response (200):**
```json
{
  "message": "Logout successful"
}
```

---

## 🎯 Summary

The ASCEND authentication system provides:

1. **Secure Registration**
   - Students: Immediate access
   - Mentors: Requires admin approval (`is_verified = False`)
   - Admins: Manual creation only

2. **Secure Login**
   - Password hashing with PBKDF2-SHA256
   - Session-based authentication
   - Remember me functionality

3. **Session Management**
   - Encrypted session cookies
   - HttpOnly and SameSite protection
   - Automatic user loading

4. **Input Validation**
   - Required field checks
   - Uniqueness validation
   - Role validation

5. **JSON Responses**
   - Consistent error messages
   - Appropriate HTTP status codes
   - User data serialization

This creates a production-ready, secure authentication system! 🔐✨
