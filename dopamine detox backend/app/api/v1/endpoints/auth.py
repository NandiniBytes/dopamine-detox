from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.core.database import get_session
from app.core.security import create_access_token, verify_password, get_password_hash
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserOut
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserOut)
async def register_user(user_in: UserCreate, session: AsyncSession = Depends(get_session)):
    """
    Register a new user.
    """
    result = await session.execute(select(User).where(User.email == user_in.email))
    db_user = result.scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_in.password)
    new_user = User(email=user_in.email, hashed_password=hashed_password, full_name=user_in.full_name)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    session: AsyncSession = Depends(get_session)
):
    """
    Authenticate user and return a JWT token.
    """
    result = await session.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

