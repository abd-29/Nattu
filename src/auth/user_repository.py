import bcrypt

from src.auth.user import User
from src.vectorstore.database import get_connection

def hash_password(password: str) -> str:
    """Hash a password."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

def get_user_by_username(username: str) -> tuple[User, str] | None:
    """Find an active user by username."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, username, email, department, role, is_active, password_hash
                FROM users
                WHERE username = %s;
                """,
                (username,),
            )
            row = cursor.fetchone()

    if row is None:
        return None

    user = User(
        id=row[0],
        username=row[1],
        email=row[2],
        department=row[3],
        role=row[4],
        is_active=row[5],
    )

    return user, row[6]

def authenticate_user(username: str, password: str) -> User | None:
    """Authenticate a user."""
    result = get_user_by_username(username)

    if result is None:
        return None

    user, password_hash = result

    if not user.is_active:
        return None

    if not verify_password(password, password_hash):
        return None

    return user


def can_access_document(user: User, department: str | None, classification: str | None) -> bool:
    """Check whether a user can access a document."""
    if classification == "public":
        return True

    if classification == "internal":
        return True

    if classification == "restricted":
        return department == user.department

    if classification == "confidential":
        return user.role == "admin"

    return False


def create_user(username: str, email: str, password: str, department: str, role: str = "employee") -> None:
    """Create a new user with a hashed password."""
    password_hash = hash_password(password)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (
                    username,
                    email,
                    password_hash,
                    department,
                    role
                )
                VALUES (%s, %s, %s, %s, %s);
                """,
                (username, email, password_hash, department, role),
            )

if __name__ == "__main__":
    create_user(
        username="bob",
        email="bob@novatech.fr",
        password="Bob123!",
        department="hr",
    )

    create_user(
        username="claire",
        email="claire@novatech.fr",
        password="Claire123!",
        department="quality",
        role="manager",
    )

    create_user(
        username="admin",
        email="admin@novatech.fr",
        password="Admin123!",
        department="direction",
        role="admin",
    )