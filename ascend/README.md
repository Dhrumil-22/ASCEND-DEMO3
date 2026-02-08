# ASCEND Flask Backend

A modular Flask backend application for the ASCEND mentorship platform.

## Features

- **User Authentication**: Registration, login, logout with Flask-Login
- **Role-Based Access**: Student, Mentor, and Admin roles with different permissions
- **Question System**: Students can ask questions, mentors can respond
- **Trust Score System**: Mentor reliability tracking based on response quality
- **Learning Roadmaps**: Personalized learning paths for students
- **Queue Management**: Intelligent question routing to mentors
- **Recommendation Engine**: Mentor recommendations based on expertise and trust scores

## Project Structure

```
ascend/
├── app.py                      # Main application file (Flask factory)
├── config.py                   # Configuration for different environments
├── database.py                 # Database initialization and utilities
├── requirements.txt            # Python dependencies
├── models/                     # Database models
│   ├── user.py                # User model (students, mentors, admins)
│   ├── question.py            # Question model
│   ├── mentor_response.py     # Mentor response model
│   ├── roadmap.py             # Learning roadmap model
│   └── trust_score.py         # Mentor trust score model
├── routes/                     # API routes (Blueprints)
│   ├── auth_routes.py         # Authentication endpoints
│   ├── student_routes.py      # Student-specific endpoints
│   ├── mentor_routes.py       # Mentor-specific endpoints
│   └── admin_routes.py        # Admin-specific endpoints
└── services/                   # Business logic services
    ├── recommendation_service.py  # Mentor recommendation algorithms
    ├── queue_service.py           # Question queue management
    └── trust_service.py           # Trust score calculations
```

## Installation

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional):
   Create a `.env` file in the project root:
   ```
   FLASK_ENV=development
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///ascend.db
   ```

## Running the Application

### Development Mode

```bash
python app.py
```

The application will run on `http://localhost:5000`

### Production Mode

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

### Authentication (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/profile` - Get current user profile
- `PUT /auth/profile` - Update user profile

### Student Routes (`/student`)
- `GET /student/questions` - Get all questions
- `POST /student/questions` - Create new question
- `GET /student/questions/<id>` - Get question details
- `GET /student/mentors` - Get recommended mentors
- `GET /student/roadmap` - Get learning roadmaps
- `POST /student/roadmap` - Create new roadmap

### Mentor Routes (`/mentor`)
- `GET /mentor/queue` - Get questions from queue
- `POST /mentor/respond/<question_id>` - Respond to question
- `GET /mentor/responses` - Get response history
- `GET /mentor/trust-score` - Get trust score
- `GET /mentor/stats` - Get performance statistics

### Admin Routes (`/admin`)
- `GET /admin/users` - List all users
- `POST /admin/verify-mentor/<id>` - Verify mentor
- `GET /admin/analytics` - Platform analytics
- `POST /admin/moderate/<question_id>` - Moderate content
- `DELETE /admin/users/<id>` - Delete user

## Database Models

### User
- Handles authentication and user profiles
- Roles: student, mentor, admin
- Integrates with Flask-Login

### Question
- Student questions with status tracking
- Categories and tags for organization
- Priority levels for queue management

### MentorResponse
- Mentor answers to questions
- Feedback tracking (helpful/not helpful)
- Upvote system

### Roadmap
- Personalized learning paths
- JSON-based milestone tracking
- Progress calculation

### TrustScore
- Mentor reliability metrics
- Automatic score calculation
- Performance analytics

## Configuration

The application supports three environments:

- **Development**: SQLite database, debug mode enabled
- **Production**: PostgreSQL/MySQL, secure cookies, debug disabled
- **Testing**: In-memory SQLite, CSRF disabled

Configure via `FLASK_ENV` environment variable or in `config.py`.

## Security Features

- Password hashing with Werkzeug
- Session management with Flask-Login
- CSRF protection
- Secure cookie settings for production
- Role-based access control

## Future Enhancements

- Database migrations with Flask-Migrate
- API documentation with Swagger
- Email notifications
- Real-time updates with WebSockets
- Advanced analytics dashboard
- Machine learning for recommendations

## License

MIT License

## Contact

For questions or support, contact the ASCEND development team.
