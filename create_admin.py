import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.security import generate_password_hash

class Base(DeclarativeBase):
    pass

# Initialize db
db = SQLAlchemy(model_class=Base)

# Create app
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
db.init_app(app)

with app.app_context():
    # Import User model
    from models import User
    
    # Check if admin field exists
    try:
        # Create admin user
        admin_username = "admin"
        admin_email = "admin@optai.com"
        admin_password = "Admin123!"  # You should change this in production
        
        # Check if admin exists
        admin = User.query.filter_by(email=admin_email).first()
        
        if admin:
            print(f"Admin user with email {admin_email} already exists.")
            print("Updating to admin status and enterprise subscription...")
            admin.is_admin = True
            admin.subscription_status = "enterprise"
            db.session.commit()
            print("Admin updated successfully.")
        else:
            # Create new admin user
            admin = User(
                username=admin_username,
                email=admin_email,
                password_hash=generate_password_hash(admin_password),
                is_admin=True,
                subscription_status="enterprise"
            )
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created successfully.")
            print(f"Username: {admin_username}")
            print(f"Email: {admin_email}")
            print(f"Password: {admin_password}")
        
    except Exception as e:
        print(f"Error creating admin user: {str(e)}")
        db.session.rollback()