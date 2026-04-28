import bcrypt


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(hash_password(sys.argv[1]))
    else:
        print("Usage: python -c \"from app.utils.admin_auth import hash_password; print(hash_password('admin123'))\"")