from sqlalchemy.orm import Session
from app.models import User
from app.core.db import SessionLocal
import sys

def make_admin(username: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            print(f"User '{username}' not found.")
            sys.exit(1)
        
        user.is_admin = True
        db.commit()
        db.refresh(user)
        print(f"Success: User '{username}' is now an admin.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/make_admin.py <username>")
        sys.exit(1)
    make_admin(sys.argv[1])
