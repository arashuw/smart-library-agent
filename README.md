\# 📚 Smart Library Agent | دستیار هوشمند کتابخانه



یک دستیار هوشمند و شخصی‌سازی‌شده کتابخانه مبتنی بر \*\*FastAPI\*\* و \*\*Google Gemini API\*\* با رابط کاربری ماژولار به سبک \*\*Swiss Modernism 2.0\*\*.



\---



\## ✨ ویژگی‌های کلیدی



\* \*\*پروفایل شخصی خواننده (Reader Profile):\*\* دریافت نام، ژانرهای مورد علاقه و هدف مطالعاتی کاربر در اولین ورود و ذخیره آن در دیتابیس برای شخصی‌سازی تمام پاسخ‌ها.

\* \*\*موتور پیشنهاد کتاب با هوش مصنوعی (AI Recommendation Engine):\*\* تحلیل کتاب‌های خوانده‌شده، امتیازها و حال‌وهوای فعلی کاربر (`Mood`) با خروجی ساختاریافته (Structured JSON Output) شامل خلاصه بدون اسپویل و دلیل پیشنهاد.

\* \*\*گفتگوی تعاملی با کتابدار هوشمند (AI Librarian Chat):\*\* چت زنده با آگاهی کامل از قفسه کتاب‌های کاربر و کتاب‌های پیشنهادی اخیر.

\* \*\*دریافت خودکار جلد کتاب‌ها:\*\* جستجو و نمایش تصویر جلد کتاب‌های پیشنهادی.

\* \*\*طراحی Swiss Modernism 2.0:\*\* رابط کاربری کاملاً راست‌به‌چپ (RTL) با گرید ۱۲ ستونه، تایپوگرافی ترکیبی فارسی و انگلیسی (`Vazirmatn` و `Cormorant Garamond`) و پالت رنگی کاغذ و چوب.



\---



\## 🛠️ فناوری‌های استفاده‌شده



\* \*\*Backend:\*\* Python, FastAPI, SQLAlchemy, SQLite, Pydantic

\* \*\*AI \& LLM:\*\* Google GenAI SDK (`gemini-3.8-flash` / `gemini-3.5-flash`)

\* \*\*Frontend:\*\* HTML5, Tailwind CSS (CDN), Vanilla JavaScript



\---



\## 📂 ساختار پروژه



```text

smart-library-agent/

├── backend/

│   ├── main.py          # اندپوینت‌های FastAPI (پروفایل، کتاب‌ها، پیشنهاد و چت)

│   ├── agent.py         # اتصال به Google Gemini SDK و پرامپت‌نویسی ساختاریافته

│   ├── models.py        # مدل‌های دیتابیس SQLAlchemy (UserProfile, UserBook, BookInsight)

│   ├── database.py      # پیکربندی SQLite

│   └── book\_fetcher.py  # دریافت تصویر جلد کتاب‌ها

├── frontend/

│   └── index.html       # رابط کاربری تک‌صفحه‌ای (Swiss Modernism 2.0)

├── .env.example         # الگوی متغیرهای محیطی

├── .gitignore           # فایل‌های مستثنی‌شده از گیت

└── README.md

