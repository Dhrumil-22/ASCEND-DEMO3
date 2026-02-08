# Authentication System - Quick Reference Card

## 🚀 Quick Start

### Start the Server
```bash
python app.py
```

### Test the Authentication
```bash
python test_auth.py
```

---

## 📍 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | ❌ | Register new user |
| POST | `/auth/login` | ❌ | Login user |
| POST | `/auth/logout` | ✅ | Logout user |
| GET | `/auth/profile` | ✅ | Get profile |
| PUT | `/auth/profile` | ✅ | Update profile |
| POST | `/auth/change-password` | ✅ | Change password |

---

## 📝 Request Examples

### Register Student
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "pass123",
    "role": "student"
  }'
```

### Register Mentor
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "bob",
    "email": "bob@example.com",
    "password": "pass456",
    "role": "mentor"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "username": "alice",
    "password": "pass123"
  }'
```

### Get Profile
```bash
curl -X GET http://localhost:5000/auth/profile \
  -H "Content-Type: application/json" \
  -b cookies.txt
```

### Logout
```bash
curl -X POST http://localhost:5000/auth/logout \
  -H "Content-Type: application/json" \
  -b cookies.txt
```

---

## 🔐 Registration Rules

### Students
- ✅ Register normally
- ✅ Immediate access to all features
- ✅ Can ask questions, view roadmaps

### Mentors
- ✅ Register with `is_verified = False`
- ⚠️ Cannot answer questions until verified
- ✅ Get TrustScore (initial: 50)
- 🔒 Need admin approval

### Admins
- ❌ Cannot register via API
- 🔧 Must be created manually
- 👑 Full platform access

---

## 🎯 Authentication Flow

```
REGISTRATION
  ↓
Validate Input
  ↓
Check Duplicates
  ↓
Hash Password
  ↓
Create User (is_verified=False for mentors)
  ↓
Save to Database
  ↓
Return User Data

LOGIN
  ↓
Find User
  ↓
Verify Password
  ↓
Create Session
  ↓
Set Cookie
  ↓
Return User Data

AUTHENTICATED REQUEST
  ↓
Read Cookie
  ↓
Load User
  ↓
Check Permissions
  ↓
Execute Route
```

---

## 🔒 Security Features

### Password Security
- ✅ PBKDF2-SHA256 hashing
- ✅ 260,000 iterations
- ✅ Random salt per password
- ✅ Cannot reverse hash

### Session Security
- ✅ Encrypted cookies
- ✅ HttpOnly (prevents XSS)
- ✅ SameSite (prevents CSRF)
- ✅ Secure in production (HTTPS)

### Input Validation
- ✅ Required fields check
- ✅ Email/username uniqueness
- ✅ Role validation
- ✅ Admin creation prevention

---

## 📊 Response Codes

| Code | Meaning | When |
|------|---------|------|
| 200 | OK | Login, logout, profile success |
| 201 | Created | Registration success |
| 400 | Bad Request | Invalid input, duplicates |
| 401 | Unauthorized | Wrong password, not logged in |
| 403 | Forbidden | Admin registration attempt |

---

## 🧪 Testing Checklist

- [ ] Register student → Success (201)
- [ ] Register mentor → Success (201, is_verified=False)
- [ ] Register admin → Fail (403)
- [ ] Duplicate username → Fail (400)
- [ ] Duplicate email → Fail (400)
- [ ] Login with correct password → Success (200)
- [ ] Login with wrong password → Fail (401)
- [ ] Access profile when logged in → Success (200)
- [ ] Access profile when logged out → Fail (401)
- [ ] Update profile → Success (200)
- [ ] Change password → Success (200)
- [ ] Logout → Success (200)

---

## 💡 Common Issues

### Issue: "Cannot connect to server"
**Solution:** Make sure Flask app is running
```bash
python app.py
```

### Issue: "Username already exists"
**Solution:** Use a different username or delete the database
```bash
rm ascend_dev.db
python app.py  # Database will be recreated
```

### Issue: "401 Unauthorized"
**Solution:** Make sure you're logged in and using cookies
```bash
# Save cookies during login
curl -c cookies.txt ...

# Use cookies in requests
curl -b cookies.txt ...
```

---

## 📚 Documentation Files

- **[AUTH_SYSTEM_GUIDE.md](AUTH_SYSTEM_GUIDE.md)** - Complete authentication guide
- **[USER_MODEL_GUIDE.md](USER_MODEL_GUIDE.md)** - User model documentation
- **[AUTH_FLOW_DIAGRAM.md](AUTH_FLOW_DIAGRAM.md)** - Visual flow diagrams
- **[test_auth.py](test_auth.py)** - Automated testing script

---

## 🎓 Key Concepts

### Password Hashing
```python
# Setting password
user.set_password('plain_password')
# Stores: 'pbkdf2:sha256:260000$salt$hash'

# Checking password
user.check_password('entered_password')
# Returns: True/False
```

### Session Management
```python
# Login
login_user(user, remember=True)
# Creates encrypted session cookie

# Access current user
current_user.username
current_user.role
current_user.is_student()

# Logout
logout_user()
# Clears session cookie
```

### Role Checking
```python
if current_user.is_student():
    # Student logic
    
if current_user.is_mentor() and current_user.is_verified:
    # Verified mentor logic
    
if current_user.is_admin():
    # Admin logic
```

---

**Ready to use!** 🚀

For detailed explanations, see [AUTH_SYSTEM_GUIDE.md](AUTH_SYSTEM_GUIDE.md)
