# Quick Start Guide for ASCEND Flask Backend

## ✅ Installation Complete!

The ASCEND Flask backend has been successfully created and tested.

## 🚀 Running the Application

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

```bash
python app.py
```

The server will start on `http://localhost:5000`

You should see output like:
```
✓ Database tables created successfully
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### Step 3: Test the API

Open your browser or use curl to test:

**Root Endpoint:**
```bash
curl http://localhost:5000/
```

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Register a User:**
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"password123\",\"role\":\"student\"}"
```

**Login:**
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"password\":\"password123\"}"
```

## 📁 Project Files Created

- **Core Files (5)**: app.py, config.py, database.py, requirements.txt, README.md
- **Models (5)**: user.py, question.py, mentor_response.py, roadmap.py, trust_score.py
- **Routes (4)**: auth_routes.py, student_routes.py, mentor_routes.py, admin_routes.py
- **Services (3)**: recommendation_service.py, queue_service.py, trust_service.py
- **Package Files (3)**: __init__.py files for models, routes, and services

## 🔧 Configuration

The app uses SQLite database by default (`ascend_dev.db` in the project directory).

To use a different database, set the environment variable:
```bash
set DEV_DATABASE_URL=postgresql://user:pass@localhost/ascend
python app.py
```

## 📚 API Documentation

See [README.md](README.md) for complete API documentation and endpoint details.

## 🐛 Troubleshooting

If you encounter any issues:

1. Make sure all dependencies are installed: `pip install -r requirements.txt`
2. Check that you're in the correct directory
3. Ensure Python 3.8+ is installed
4. Delete `ascend_dev.db` and restart if database issues occur

## ✨ Features

- ✅ User authentication with password hashing
- ✅ Role-based access control (Student/Mentor/Admin)
- ✅ Question & Answer system
- ✅ Trust score tracking for mentors
- ✅ Learning roadmaps with milestones
- ✅ Intelligent mentor recommendations
- ✅ Priority-based question queue

## 🎯 Next Steps

1. Test the API endpoints using Postman or curl
2. Create some test users (students, mentors, admins)
3. Explore the different role-based endpoints
4. Review the code documentation in each file
5. Customize the trust score algorithm in `services/trust_service.py`
6. Add frontend integration

Enjoy building with ASCEND! 🚀
