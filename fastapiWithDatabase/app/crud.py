from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User, Post
from app.schemas import UserCreate, PostCreate
from app.security import hash_password

async def get_user_by_email(db: AsyncSession, email: str):
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_post(db: AsyncSession, post: PostCreate, user_id: int):
    db_post = Post(title=post.title, content=post.content, author_id=user_id)
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    return db_post

async def get_all_posts(db: AsyncSession):
    stmt = select(Post)
    result = await db.execute(stmt)
    return result.scalars().all()