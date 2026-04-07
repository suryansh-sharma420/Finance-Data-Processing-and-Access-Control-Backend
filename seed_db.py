import os
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.db.models.user import User
from app.db.models.role import Role
from app.db.models.record import Record
from app.core import security
from datetime import datetime

def seed_database():
    """Seeds the SQLite database with initial system users and financial records using String Enums."""
    print("Recreating database schema...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 1. Seed Roles (Optional check, but useful)
        roles = ["Admin", "Viewer", "Analyst"]
        for role_name in roles:
            # Simple check or just add
            role = Role(name=role_name)
            db.add(role)
        db.commit()
        print(f"✅ roles seeded: {roles}")

        # 2. Seed Mock Users
        users_to_seed = [
            {"email": "admin@zorvyn.com", "username": "admin_user", "role": "Admin", "password": "password123", "is_superuser": True},
            {"email": "analyst@zorvyn.com", "username": "analyst_user", "role": "Analyst", "password": "password123", "is_superuser": False},
            {"email": "viewer@zorvyn.com", "username": "viewer_user", "role": "Viewer", "password": "password123", "is_superuser": False}
        ]

        user_objects = []
        for u_data in users_to_seed:
            hashed_pwd = security.get_password_hash(u_data["password"])
            new_user = User(
                email=u_data["email"],
                username=u_data["username"],
                role=u_data["role"],
                hashed_password=hashed_pwd,
                is_active=True,
                is_superuser=u_data["is_superuser"]
            )
            db.add(new_user)
            user_objects.append(new_user)
        db.commit()
        print(f"✅ Mock Users seeded: {[u['email'] for u in users_to_seed]}")

        # 3. Seed Sample Records (Option A: Using String Enums directly)
        if user_objects:
            # Categories: "Salary", "Other Income", "Housing", "Food", "Transportation", "Misc"
            sample_records = [
                {"type": "Income", "amount": 5500.0, "description": "Monthly Salary", "user_id": user_objects[0].id, "category": "Salary"},
                {"type": "Expense", "amount": 1500.0, "description": "Home Rent", "user_id": user_objects[0].id, "category": "Housing"},
                {"type": "Expense", "amount": 350.0, "description": "Grocery Shopping", "user_id": user_objects[0].id, "category": "Food"},
                {"type": "Expense", "amount": 120.0, "description": "Train Monthly Pass", "user_id": user_objects[0].id, "category": "Transportation"},
            ]
            for r_data in sample_records:
                new_record = Record(**r_data, date=datetime.utcnow())
                db.add(new_record)
            db.commit()
            print("✅ Sample Records seeded for admin user.")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
