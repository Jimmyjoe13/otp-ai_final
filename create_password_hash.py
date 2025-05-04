from werkzeug.security import generate_password_hash

password = "Admin123!"
password_hash = generate_password_hash(password)

print(f"Password: {password}")
print(f"Hash: {password_hash}")