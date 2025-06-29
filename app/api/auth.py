# app/api/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from jose import JWTError
from datetime import timedelta

from app.core.models import Users
from app.db.init_db import engine
from app.security import verify_password, create_access_token, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES, hash_password
from app.core.schemas import Token, TokenData, UserCreate, UserRead

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

@router.post("/users", response_model=UserRead)
def register(u: UserCreate):
    with Session(engine) as session:
        exists = session.exec(select(Users).where(Users.email == u.email)).first()
        if exists:
            raise HTTPException(status_code=400, detail="Email already registered")
        user = Users(
            email=u.email,
            name=u.name,
            hashed_password=hash_password(u.password)
        )
        session.add(user)
        session.commit()
        session.refresh(user)
    return user

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception

    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.user_id == token_data.user_id)).first()
    if user is None:
        raise credentials_exception
    return user
