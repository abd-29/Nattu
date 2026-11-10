from src.auth.user_repository import hash_password, verify_password

def test_password_hashing():
    password = "Alice123!"
    password_hash = hash_password(password)
    assert password_hash != password
    assert verify_password(password, password_hash)

def test_wrong_password():
    password_hash = hash_password("Alice123!")
    assert not verify_password("WrongPassword", password_hash)