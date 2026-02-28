from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import UserCreate, UserResponse, PostCreate, PostResponse, Token
from app.crud import get_user_by_email, create_user, create_post, get_all_posts
from app.security import verify_password, create_access_token

router = APIRouter()

# --- AUTH & USERS ---
@router.post("/users/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await create_user(db=db, user=user)

@router.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, email=form_data.username) # OAuth2 uses 'username' for the email field
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# --- POSTS ---
@router.post("/posts/", response_model=PostResponse)
async def make_post(post: PostCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await create_post(db=db, post=post, user_id=current_user.id)

@router.get("/posts/", response_model=List[PostResponse])
async def read_posts(db: AsyncSession = Depends(get_db)):
    return await get_all_posts(db=db)