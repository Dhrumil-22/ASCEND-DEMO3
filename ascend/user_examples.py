"""
User Model Examples - Practical Usage Guide

This file demonstrates how to use the User model in various scenarios.
Run this file to see examples of user creation, authentication, and role management.
"""

from app import create_app
from database import db
from models.user import User
from models.trust_score import TrustScore
from flask_login import login_user, current_user

# Create app context
app = create_app()


def example_1_create_users():
    """Example 1: Creating different types of users"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Creating Users")
    print("="*60)
    
    with app.app_context():
        # Create a student
        student = User(
            username='alice_student',
            email='alice@example.com',
            role='student',
            full_name='Alice Johnson',
            bio='Aspiring Python developer'
        )
        student.set_password('student_password_123')
        
        db.session.add(student)
        db.session.commit()
        
        print(f"\n✓ Created Student: {student}")
        print(f"  - ID: {student.id}")
        print(f"  - Username: {student.username}")
        print(f"  - Role: {student.role}")
        print(f"  - Password Hash: {student.password_hash[:50]}...")
        
        # Create a mentor
        mentor = User(
            username='bob_mentor',
            email='bob@example.com',
            role='mentor',
            full_name='Bob Smith',
            bio='Senior Python Developer with 10 years experience',
            expertise='Python, Django, Flask, Machine Learning'
        )
        mentor.set_password('mentor_password_456')
        
        db.session.add(mentor)
        db.session.commit()
        
        # Create trust score for mentor
        trust_score = TrustScore(mentor_id=mentor.id)
        db.session.add(trust_score)
        db.session.commit()
        
        print(f"\n✓ Created Mentor: {mentor}")
        print(f"  - ID: {mentor.id}")
        print(f"  - Username: {mentor.username}")
        print(f"  - Role: {mentor.role}")
        print(f"  - Expertise: {mentor.get_expertise_list()}")
        print(f"  - Verified: {mentor.is_verified}")
        print(f"  - Trust Score: {mentor.trust_score.score}")
        
        # Create an admin
        admin = User(
            username='admin_user',
            email='admin@ascend.com',
            role='admin',
            full_name='Admin User'
        )
        admin.set_password('admin_password_789')
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"\n✓ Created Admin: {admin}")
        print(f"  - ID: {admin.id}")
        print(f"  - Username: {admin.username}")
        print(f"  - Role: {admin.role}")


def example_2_password_verification():
    """Example 2: Password hashing and verification"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Password Verification")
    print("="*60)
    
    with app.app_context():
        # Find a user
        user = User.query.filter_by(username='alice_student').first()
        
        if user:
            print(f"\nTesting password for user: {user.username}")
            
            # Correct password
            correct_password = 'student_password_123'
            if user.check_password(correct_password):
                print(f"✓ Correct password '{correct_password}' verified!")
            else:
                print(f"✗ Password verification failed")
            
            # Wrong password
            wrong_password = 'wrong_password'
            if user.check_password(wrong_password):
                print(f"✓ Password '{wrong_password}' verified")
            else:
                print(f"✗ Wrong password '{wrong_password}' rejected (as expected)")
            
            # Show that same password creates different hashes
            print(f"\nPassword Hash Uniqueness:")
            print(f"Original hash: {user.password_hash[:60]}...")
            
            # Create new user with same password
            temp_user = User(username='temp', email='temp@ex.com')
            temp_user.set_password(correct_password)
            print(f"New hash:      {temp_user.password_hash[:60]}...")
            print(f"Hashes are different due to random salt!")


def example_3_role_checking():
    """Example 3: Role-based logic"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Role-Based Logic")
    print("="*60)
    
    with app.app_context():
        users = User.query.all()
        
        for user in users:
            print(f"\nUser: {user.username}")
            print(f"  Role: {user.role}")
            
            if user.is_student():
                print(f"  → Can ask questions")
                print(f"  → Can view roadmaps")
                print(f"  → Can rate mentors")
            
            elif user.is_mentor():
                print(f"  → Can answer questions: {user.is_verified}")
                print(f"  → Expertise: {user.get_expertise_list()}")
                if user.trust_score:
                    print(f"  → Trust Score: {user.trust_score.score}")
            
            elif user.is_admin():
                print(f"  → Can verify mentors")
                print(f"  → Can moderate content")
                print(f"  → Full platform access")


def example_4_mentor_verification():
    """Example 4: Admin verifying a mentor"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Mentor Verification")
    print("="*60)
    
    with app.app_context():
        # Get admin and mentor
        admin = User.query.filter_by(role='admin').first()
        mentor = User.query.filter_by(role='mentor').first()
        
        if admin and mentor:
            print(f"\nAdmin: {admin.username}")
            print(f"Mentor: {mentor.username}")
            print(f"Mentor verified status: {mentor.is_verified}")
            
            # Admin verifies mentor
            if admin.is_admin():
                print(f"\n{admin.username} is verifying {mentor.username}...")
                mentor.is_verified = True
                db.session.commit()
                print(f"✓ Mentor verified!")
                print(f"New verified status: {mentor.is_verified}")
            else:
                print(f"✗ {admin.username} is not an admin!")


def example_5_user_serialization():
    """Example 5: Converting user to dictionary (for JSON API)"""
    print("\n" + "="*60)
    print("EXAMPLE 5: User Serialization")
    print("="*60)
    
    with app.app_context():
        mentor = User.query.filter_by(role='mentor').first()
        
        if mentor:
            # Without email (public view)
            public_data = mentor.to_dict(include_email=False)
            print(f"\nPublic user data (no email):")
            for key, value in public_data.items():
                print(f"  {key}: {value}")
            
            # With email (private view)
            private_data = mentor.to_dict(include_email=True)
            print(f"\nPrivate user data (with email):")
            for key, value in private_data.items():
                print(f"  {key}: {value}")
            
            print(f"\nNote: password_hash is NEVER included in serialization!")


def example_6_updating_user():
    """Example 6: Updating user profile"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Updating User Profile")
    print("="*60)
    
    with app.app_context():
        mentor = User.query.filter_by(role='mentor').first()
        
        if mentor:
            print(f"\nOriginal mentor data:")
            print(f"  Full name: {mentor.full_name}")
            print(f"  Bio: {mentor.bio}")
            print(f"  Expertise: {mentor.get_expertise_list()}")
            
            # Update profile
            mentor.full_name = "Robert 'Bob' Smith"
            mentor.bio = "Senior Python Developer with 15 years experience"
            mentor.set_expertise_list([
                'Python',
                'Django',
                'Flask',
                'Machine Learning',
                'Data Science',
                'AWS'
            ])
            
            db.session.commit()
            
            print(f"\nUpdated mentor data:")
            print(f"  Full name: {mentor.full_name}")
            print(f"  Bio: {mentor.bio}")
            print(f"  Expertise: {mentor.get_expertise_list()}")
            print(f"  Updated at: {mentor.updated_at}")


def example_7_querying_users():
    """Example 7: Querying users by role"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Querying Users")
    print("="*60)
    
    with app.app_context():
        # Get all students
        students = User.query.filter_by(role='student').all()
        print(f"\nStudents ({len(students)}):")
        for student in students:
            print(f"  - {student.username} ({student.full_name})")
        
        # Get all verified mentors
        verified_mentors = User.query.filter_by(
            role='mentor',
            is_verified=True
        ).all()
        print(f"\nVerified Mentors ({len(verified_mentors)}):")
        for mentor in verified_mentors:
            print(f"  - {mentor.username} ({mentor.full_name})")
            print(f"    Expertise: {', '.join(mentor.get_expertise_list())}")
        
        # Get all admins
        admins = User.query.filter_by(role='admin').all()
        print(f"\nAdmins ({len(admins)}):")
        for admin in admins:
            print(f"  - {admin.username}")


def example_8_authentication_flow():
    """Example 8: Simulating login flow"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Authentication Flow Simulation")
    print("="*60)
    
    with app.app_context():
        # Simulate login attempt
        username_input = 'alice_student'
        password_input = 'student_password_123'
        
        print(f"\nLogin attempt:")
        print(f"  Username: {username_input}")
        print(f"  Password: {'*' * len(password_input)}")
        
        # Step 1: Find user
        user = User.query.filter(
            (User.username == username_input) | (User.email == username_input)
        ).first()
        
        if not user:
            print(f"\n✗ User not found!")
            return
        
        print(f"\n✓ User found: {user.username}")
        
        # Step 2: Verify password
        if not user.check_password(password_input):
            print(f"✗ Invalid password!")
            return
        
        print(f"✓ Password verified!")
        
        # Step 3: Check if account is active
        # (In this example, all accounts are active)
        print(f"✓ Account is active")
        
        # Step 4: Login successful
        print(f"\n✓ Login successful!")
        print(f"  User ID: {user.id}")
        print(f"  Role: {user.role}")
        print(f"  Session would be created here")


def run_all_examples():
    """Run all examples"""
    print("\n" + "="*70)
    print(" "*15 + "USER MODEL EXAMPLES")
    print("="*70)
    
    try:
        example_1_create_users()
        example_2_password_verification()
        example_3_role_checking()
        example_4_mentor_verification()
        example_5_user_serialization()
        example_6_updating_user()
        example_7_querying_users()
        example_8_authentication_flow()
        
        print("\n" + "="*70)
        print(" "*20 + "ALL EXAMPLES COMPLETED!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    # Run all examples
    run_all_examples()
