from dataclasses import dataclass

@dataclass
class User:
    id: int
    username: str
    email: str
    department: str
    role: str
    is_active: bool