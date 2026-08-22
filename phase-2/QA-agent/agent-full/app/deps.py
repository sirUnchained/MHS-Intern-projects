from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import sessionmaker, Session

from app.core.engine import get_engine
from app.core.security import decode_access_token
from app.features.auth.models import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_db():
    """
    Yield a database session for dependency injection.

    Creates a new session and ensures it's properly closed after use.

    Yields:
        Session: SQLAlchemy database session.

    Note:
        Designed for FastAPI dependency injection with automatic cleanup.
    """

    engine = get_engine()
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        token (str): JWT access token from Authorization header.
        db (Session): Database session for user lookup.

    Returns:
        User: The authenticated user object.

    Raises:
        HTTPException: 401 if token is invalid or user not found.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise credentials_exception

    user = db.query(User).filter(User.username == payload["sub"]).first()
    if user is None:
        raise credentials_exception
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """
    Require admin privileges for access.

    Args:
        user (User): The current authenticated user.

    Returns:
        User: The user if they have admin role.

    Raises:
        HTTPException: 403 if user is not an admin.
    """

    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return user
