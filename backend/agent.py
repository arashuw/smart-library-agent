import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

CANDIDATE_MODELS = [
    "models/gemini-3.8-flash",
    "models/gemini-3.7-flash",
    "models/gemini-3.5-flash",
    "models/gemini-3.1-flash-lite"
]

class RecommendedBook(BaseModel):
    title: str = Field(description="عنوان دقیق کتاب (ترجیحاً فارسی و در پرانتز عنوان اصلی انگلیسی)")
    english_title: str = Field(description="عنوان اصلی کتاب به انگلیسی برای جستجوی تصویر جلد")
    author: str = Field(description="نام نویسنده")
    reason: str = Field(description="دلیل شخصی‌سازی‌شده که چرا بر اساس علایق و نمرات کاربر پیشنهاد شده")
    spoiler_free_summary: str = Field(description="تصویر کلی از داستان یا محتوای کتاب در ۳ تا ۴ جمله بدون اسپویل")
    vibe_tags: list[str] = Field(description="۳ تا ۴ برچسب کوتاه از حال‌وهوای کتاب، مثلاً: فلسفی، پرتعلیق")
    target_audience: str = Field(description="این کتاب مناسب چه کسانی است")

class RecommendationResponse(BaseModel):
    taste_analysis: str = Field(description="تحلیل کوتاه ۲ جمله‌ای از سلیقه مطالعاتی فعلی کاربر")
    recommendations: list[RecommendedBook] = Field(description="لیست ۳ کتاب پیشنهادی هوشمند")

def _format_user_books(user_books: list[dict]) -> str:
    if not user_books:
        return "کاربر هنوز کتابی ثبت نکرده است."
    lines = []
    for b in user_books:
        status_label = "خوانده‌شده" if b.get("status") == "read" else "در لیست مطالعه"
        rating_str = f"امتیاز: {b['rating']}/5" if b.get('rating') else "بدون امتیاز"
        review_str = f"نظر: {b['review']}" if b.get('review') else ""
        lines.append(f"- [{status_label}] «{b['title']}» اثر {b['author']} ({rating_str}) {review_str}")
    return "\n".join(lines)

def get_book_recommendations(user_books: list[dict], custom_mood: str = "") -> dict:
    """تحلیل کتاب‌های کاربر و تولید پیشنهادهای هوشمند"""
    history_text = _format_user_books(user_books)
    mood_instruction = f"\nدرخواست یا حال‌وهوای فعلی کاربر: {custom_mood}" if custom_mood else ""

    prompt = f"""
    تو یک مشاور هوشمند و خبره کتابخانه هستی. بر اساس لیست کتاب‌هایی که کاربر قبلاً خوانده، امتیازهایی که داده و نظراتش، سلیقه دقیق او را تحلیل کن و ۳ کتاب جدید (که در لیست قبلی او نیستند) پیشنهاد بده.
    
    سابقه مطالعاتی کاربر:
    {history_text}
    {mood_instruction}
    
    پاسخ را کاملاً به زبان فارسی روان، جذاب و حرفه‌ای بنویس.
    """

    last_error = None
    for model_name in CANDIDATE_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=RecommendationResponse,
                    temperature=0.7,
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            last_error = e
            continue

    raise last_error

def chat_with_librarian(user_books: list[dict], user_message: str, recent_recommendations: str = "") -> str:
    """گفتگوی تعاملی با ایجنت کتابخانه"""
    history_text = _format_user_books(user_books)
    rec_context = f"\nکتاب‌هایی که همین الان به کاربر پیشنهاد شده‌اند:\n{recent_recommendations}" if recent_recommendations else ""

    prompt = f"""
    تو یک مشاور کتابخانه باهوش، خوش‌برخورد و دقیق هستی. کاربر درباره کتاب‌ها یا پیشنهادهای اخیر سؤالی پرسیده است.
    با توجه به سابقه مطالعاتی او و پیشنهادهای فعلی، پاسخی کوتاه، دقیق، کاربردی و بدون اسپویل به زبان فارسی بده.

    سابقه کتابخانه کاربر:
    {history_text}
    {rec_context}

    سؤال کاربر: {user_message}
    """

    last_error = None
    for model_name in CANDIDATE_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7),
            )
            return response.text
        except Exception as e:
            last_error = e
            continue

    raise last_error