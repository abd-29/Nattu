from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel

from config import API_SECRET_KEY, DATA_DIR
from src.auth.user import User
from src.auth.user_repository import authenticate_user, get_user_by_username
from src.embeddings.embedding_model import load_embedding_model
from src.indexing.index_state import load_index_state
from src.retrieval.hybrid_search import answer_query
from src.retrieval.reranker import load_reranker


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

app = FastAPI(
    title="Nattu RAG API",
    description="Nattu RAG assistant API",
    version="2.0.0",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    username: str
    email: str
    department: str
    role: str


class ChatRequest(BaseModel):
    query: str


class SourceResponse(BaseModel):
    document_id: str
    version: str
    start_page: int | None = None
    end_page: int | None = None


class ChatResponse(BaseModel):
    status: str
    answer: str
    sources: list[SourceResponse]


@lru_cache
def get_embedding_model():
    """Load the embedding model once."""
    return load_embedding_model()


@lru_cache
def get_reranker():
    """Load the reranker once."""
    return load_reranker()


@lru_cache
def get_index_state():
    """Load the document index state once."""
    index_state_path = DATA_DIR / "processed" / "index_state.json"
    return load_index_state(index_state_path)


def create_access_token(username: str) -> str:
    """Create a signed JWT access token."""
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": username,
        "exp": expiration,
    }

    return jwt.encode(payload, API_SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """Retrieve the authenticated user from a JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, API_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    result = get_user_by_username(username)

    if result is None:
        raise credentials_exception

    user, _ = result

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user.")

    return user


@app.get("/health")
def health():
    """Check API availability."""
    return {
        "status": "ok",
        "service": "Nattu RAG API",
    }


@app.post("/login", response_model=TokenResponse)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Authenticate a user and return a JWT access token."""
    user = authenticate_user(form_data.username, form_data.password)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(username=user.username)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.get("/me", response_model=UserResponse)
def me(user: Annotated[User, Depends(get_current_user)]):
    """Return information about the authenticated user."""
    return {
        "username": user.username,
        "email": user.email,
        "department": user.department,
        "role": user.role,
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, user: Annotated[User, Depends(get_current_user)]):
    """Ask a question to the Nattu RAG assistant."""
    result = answer_query(
        query=request.query,
        embedding_model=get_embedding_model(),
        reranker=get_reranker(),
        index_state=get_index_state(),
        user=user,
    )

    sources = [
        {
            "document_id": source["document_id"],
            "version": source["version"],
            "start_page": source.get("start_page"),
            "end_page": source.get("end_page"),
        }
        for source in result["results"]
    ]

    return {
        "status": result["status"],
        "answer": result["answer"],
        "sources": sources,
    }