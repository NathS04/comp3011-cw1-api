from app.core import auth
try:
    hash = auth.get_password_hash("password123")
    print(f"Hash success: {hash}")
    verify = auth.verify_password("password123", hash)
    print(f"Verify success: {verify}")
except Exception as e:
    print(f"Error: {e}")
