from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter()

# function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/status")
def get_status():
    return {"status": "ok"}

@router.get("/testdb")
def test_db(db: Session = Depends(get_db)):
    try:
        result = db.execute(text("SHOW TABLES;"))  # list tables in your DB
        tables = [row[0] for row in result]
        return {"connected": True, "tables": tables}
    except Exception as e:
        return {"connected": False, "error": str(e)}
@router.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    hashed_pw = hash_password(password)
    query = text("INSERT INTO users (username, password) VALUES (:u, :p)")
    try:
        db.execute(query, {"u": username, "p": hashed_pw})
        db.commit()
        return {"success": True, "msg": "User registered!"}
    except Exception as e:
        return {"success": False, "error": str(e)}
@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    query = text("SELECT * FROM users WHERE username=:u")
    result = db.execute(query, {"u": username}).fetchone()
    if not result:
        return {"success": False, "msg": "User not found"}

    if not verify_password(password, result.password):
        return {"success": False, "msg": "Wrong password"}

    token = create_access_token({"sub": username})
    return {"success": True, "access_token": token, "token_type": "bearer"}
