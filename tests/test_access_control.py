from src.auth.user import User
from src.auth.user_repository import can_access_document

alice = User(
    id=1,
    username="Alice",
    email="alice@novatech.fr",
    department="support",
    role="employee",
    is_active=True,
)

admin = User(
    id=4,
    username="Admin",
    email="admin@novatech.fr",
    department="direction",
    role="admin",
    is_active=True,
)

def test_public_access():
    assert can_access_document(alice, "hr", "public")

def test_internal_access():
    assert can_access_document(alice, "quality", "internal")

def test_restricted_same_department():
    assert can_access_document(alice, "support", "restricted")

def test_restricted_other_department():
    assert not can_access_document(alice, "hr", "restricted")

def test_confidential_employee():
    assert not can_access_document(alice, "support", "confidential")

def test_confidential_admin():
    assert can_access_document(admin, "hr", "confidential")