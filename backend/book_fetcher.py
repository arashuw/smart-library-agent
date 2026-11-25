import requests

def fetch_book_cover(title: str, author: str = "") -> str | None:
    """جستجو در Google Books و Open Library برای یافتن باکیفیت‌ترین تصویر جلد"""
    clean_title = title.split("(")[0].strip()

    # ۱. تلاش اول: جستجو در Google Books API (پشتیبانی عالی از کتاب‌های فارسی و انگلیسی)
    try:
        gb_url = "https://www.googleapis.com/books/v1/volumes"
        gb_params = {"q": f"{title} {author}".strip(), "maxResults": 1}
        res = requests.get(gb_url, params=gb_params, timeout=5)
        if res.status_code == 200:
            items = res.json().get("items", [])
            if items:
                image_links = items[0].get("volumeInfo", {}).get("imageLinks", {})
                cover = image_links.get("thumbnail") or image_links.get("smallThumbnail")
                if cover:
                    return cover.replace("http://", "https://")
    except Exception as e:
        print(f"Google Books error for {title}: {e}")

    # ۲. تلاش دوم: جستجو در Open Library فقط با عنوان کتاب
    try:
        ol_url = "https://openlibrary.org/search.json"
        ol_params = {"title": clean_title, "limit": 1}
        res = requests.get(ol_url, params=ol_params, timeout=5)
        if res.status_code == 200:
            docs = res.json().get("docs", [])
            if docs and "cover_i" in docs[0]:
                cover_id = docs[0]["cover_i"]
                return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
    except Exception as e:
        print(f"Open Library error for {title}: {e}")

    return None