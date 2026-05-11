import bcrypt

password = "admin123"
stored_hash = "$2b$12$apxEVURs44y4pcd3JN7L9uPT9aWl2DrVW3hlHbqqJxPG8QbhR3Qei"

result = bcrypt.checkpw(password.encode(), stored_hash.encode())
print(f"Password verification result: {result}")
print(f"Expected: True")
