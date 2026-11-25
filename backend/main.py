from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from .database import engine, get_db, Base
from .models import UserBook, BookInsight
from .agent import get_book_recommendations, chat_with_librarian
from .book_fetcher import fetch_book_cover

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Library Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BookCreate(BaseModel):
    title: str
    author: str
    status: str = "read"
    rating: Optional[float] = None
    review: Optional[str] = None

class BookStatusUpdate(BaseModel):
    status: str
    rating: Optional[float] = None

class RecommendRequest(BaseModel):
    custom_mood: Optional[str] = ""

class ChatRequest(BaseModel):
    message: str
    recent_recommendations: Optional[str] = ""

@app.get("/")
def read_root():
    return {"message": "Smart Library Agent Backend is Running!"}

@app.post("/books/")
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    new_book = UserBook(
        title=book.title,
        author=book.author,
        status=book.status,
        rating=book.rating,
        review=book.review
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.get("/books/")
def get_books(db: Session = Depends(get_db)):
    return db.query(UserBook).order_by(UserBook.created_at.desc()).all()

@app.patch("/books/{book_id}/status")
def update_book_status(book_id: int, data: BookStatusUpdate, db: Session = Depends(get_db)):
    book = db.query(UserBook).filter(UserBook.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="کتاب پیدا نشد")
    book.status = data.status
    if data.rating is not None:
        book.rating = data.rating
    db.commit()
    db.refresh(book)
    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(UserBook).filter(UserBook.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="کتاب پیدا نشد")
    db.delete(book)
    db.commit()
    return {"message": "کتاب حذف شد"}

@app.post("/recommend/")
def recommend_books(req: RecommendRequest, db: Session = Depends(get_db)):
    books = db.query(UserBook).all()
    user_books_data = [
        {
            "title": b.title,
            "author": b.author,
            "status": b.status,
            "rating": b.rating,
            "review": b.review
        }
        for b in books
    ]
    
    ai_result = get_book_recommendations(user_books_data, req.custom_mood)
    
    for rec in ai_result.get("recommendations", []):
        cover = fetch_book_cover(rec.get("english_title", rec["title"]), rec["author"])
        rec["cover_url"] = cover
        
        existing = db.query(BookInsight).filter(BookInsight.title == rec["title"]).first()
        if not existing:
            insight = BookInsight(
                title=rec["title"],
                author=rec["author"],
                spoiler_free_summary=rec["spoiler_free_summary"],
                vibe_tags=", ".join(rec.get("vibe_tags", [])),
                target_audience=rec["target_audience"],
                cover_url=cover
            )
            db.add(insight)
    
    db.commit()
    return ai_result

@app.post("/chat/")
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    books = db.query(UserBook).all()
    user_books_data = [
        {
            "title": b.title,
            "author": b.author,
            "status": b.status,
            "rating": b.rating,
            "review": b.review
        }
        for b in books
    ]
    reply = chat_with_librarian(user_books_data, req.message, req.recent_recommendations)
    return {"reply": reply}