from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.deps import get_db
from app.features.auth.models import User, UserRole
from app.features.auth.schemas import UserCreate, UserOut, Token
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserOut,
    summary="Create a new account",
    description=(
        "Register a new user. The very first account created becomes an "
        "admin automatically; every account after that is a regular user."
    ),
)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Simplest possible bootstrap: the very first account becomes admin,
    # everyone after that is a normal user. There's no promote-to-admin
    # route here on purpose -- add one later if you need it.
    is_first_user = db.query(User).count() == 0
    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role=UserRole.admin if is_first_user else UserRole.user,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Log in and get a JWT",
    description=(
        "Exchange a username/password for a JWT access token. "
        "In Swagger, use the 'Authorize' button and paste this token "
        "to call protected endpoints from this page."
    ),
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token({"sub": user.username, "role": user.role.value})
    return Token(access_token=token)
