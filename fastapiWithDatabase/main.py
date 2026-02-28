from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, select

# --- 1. DATABASE SETUP (SQLite) ---
DATABASE_URL = "sqlite+aiosqlite:///./portfolio_test.db"
engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

# --- 2. SQLALCHEMY MODEL (The Database Table) ---
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)

# --- 3. PYDANTIC SCHEMA (The JSON Validator) ---
class UserCreate(BaseModel):
    email: str
    password: str

# --- 4. FASTAPI DEPENDENCY (Opens/Closes DB Sessions) ---
async def get_db():
    async with SessionLocal() as session:
        yield session

# --- 5. APP STARTUP (Creates the database file automatically!) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

# --- 6. THE ROUTES ---
@app.post("/users/")
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # 1. Stage the data
    new_user = User(email=user.email, password=user.password)
    db.add(new_user)
    
    try:
        # 2. Commit to database
        await db.commit()
        await db.refresh(new_user)
        return {"message": "User created successfully!", "user_id": new_user.id, "email": new_user.email}
    except Exception:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")

@app.get("/users/")
async def get_all_users(db: AsyncSession = Depends(get_db)):
    # Fetch all users from SQLite
    result = await db.execute(select(User))
    return result.scalars().all()