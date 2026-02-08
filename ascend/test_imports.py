import sys
import traceback

print("="* 60)
print("ASCEND App Debug Script")
print("=" * 60)

try:
    print("\n1. Testing config import...")
    from config import config
    print("   OK - Config imported")
    
    print("\n2. Testing database import...")
    from database import db
    print(f"   OK - Database imported: {db}")
    
    print("\n3. Testing Flask import...")
    from flask import Flask
    print("   OK - Flask imported")
    
    print("\n4. Testing Flask-Login import...")
    from flask_login import LoginManager
    print("   OK - Flask-Login imported")
    
    print("\n5. Testing model imports...")
    from models.user import User
    print("   OK - User model imported")
    
    print("\n6. Creating Flask app...")
    from app import create_app
    print("   OK - create_app imported")
    
    print("\n7. Calling create_app()...")
    app = create_app()
    print(f"   OK - App created: {app}")
    
    print("\n" + "=" * 60)
    print("SUCCESS - ALL TESTS PASSED!")
    print("=" * 60)
    
except Exception as e:
    print("\n" + "=" * 60)
    print("ERROR OCCURRED")
    print("=" * 60)
    print(f"\nError Type: {type(e).__name__}")
    print(f"Error Message: {str(e)}")
    print("\nFull Traceback:")
    print("-" * 60)
    traceback.print_exc()
    print("-" * 60)
    sys.exit(1)
