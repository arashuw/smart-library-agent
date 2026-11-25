const API_URL = "http://127.0.0.1:8000";

const bookForm = document.getElementById("book-form");
const userBooksList = document.getElementById("user-books-list");
const bookCount = document.getElementById("book-count");
const recommendBtn = document.getElementById("recommend-btn");
const loadingBox = document.getElementById("loading");
const tasteBox = document.getElementById("taste-box");
const tasteText = document.getElementById("taste-text");
const recGrid = document.getElementById("recommendations-grid");

const chatForm = document.getElementById("chat-form");
const chatInput = document.getElementById("chat-input");
const chatMessages = document.getElementById("chat-messages");

let lastRecommendedBooks = [];

// تولید کاور گرافیکی پیش‌فرض آفلاین (SVG) در صورت نبود تصویر جلد
function createFallbackCover(title) {
    const shortTitle = title.length > 28 ? title.substring(0, 28) + "..." : title;
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250" viewBox="0 0 400 250">
        <defs>
            <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#1e293b"/>
                <stop offset="100%" stop-color="#0f172a"/>
            </linearGradient>
        </defs>
        <rect width="400" height="250" fill="url(#g)"/>
        <rect x="20" y="20" width="360" height="210" rx="12" fill="none" stroke="#38bdf8" stroke-width="2" stroke-opacity="0.4"/>
        <text x="200" y="105" font-family="Tahoma, sans-serif" font-size="36" fill="#38bdf8" text-anchor="middle">📖</text>
        <text x="200" y="155" font-family="Tahoma, sans-serif" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">${shortTitle}</text>
    </svg>`;
    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
}

// دریافت و نمایش لیست کتاب‌های کاربر
async function loadUserBooks() {
    try {
        const res = await fetch(`${API_URL}/books/`);
        const books = await res.json();
        bookCount.textContent = books.length;
        userBooksList.innerHTML = "";

        books.forEach(book => {
            const isRead = book.status === "read";
            const badgeHtml = isRead
                ? `<span class="status-badge badge-read">✅ خوانده‌شده</span>`
                : `<span class="status-badge badge-wishlist">🔖 لیست مطالعه</span>`;

            const markReadBtn = !isRead
                ? `<button class="mark-read-btn" onclick="markAsRead(${book.id})" title="تغییر به خوانده‌شده">خواندم ✓</button>`
                : "";

            const div = document.createElement("div");
            div.className = "user-book-item";
            div.innerHTML = `
                <div class="user-book-info">
                    ${badgeHtml}
                    <h4>${book.title}</h4>
                    <span>✍️ ${book.author} ${book.rating ? `| ⭐ ${book.rating}/5` : ""}</span>
                    ${book.review ? `<p class="user-book-review">«${book.review}»</p>` : ""}
                </div>
                <div class="book-actions">
                    <button class="delete-btn" onclick="deleteBook(${book.id})" title="حذف">🗑️</button>
                    ${markReadBtn}
                </div>
            `;
            userBooksList.appendChild(div);
        });
    } catch (err) {
        console.error("خطا در دریافت کتاب‌ها:", err);
    }
}

// ثبت کتاب جدید
bookForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("title").value.trim();
    const author = document.getElementById("author").value.trim();
    const status = document.getElementById("status").value;
    const ratingVal = document.getElementById("rating").value;
    const review = document.getElementById("review").value.trim();

    const payload = {
        title,
        author,
        status,
        rating: ratingVal ? parseFloat(ratingVal) : null,
        review: review || null
    };

    try {
        await fetch(`${API_URL}/books/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        bookForm.reset();
        loadUserBooks();
    } catch (err) {
        alert("خطا در ثبت کتاب! مطمئن شوید سرور بک‌اند روشن است.");
    }
});

// افزودن کتاب پیشنهادی به لیست مطالعه
async function addToWishlist(title, author) {
    try {
        await fetch(`${API_URL}/books/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, author, status: "wishlist" })
        });
        loadUserBooks();
        alert(`کتاب «${title}» به لیست مطالعه شما اضافه شد!`);
    } catch (err) {
        alert("خطا در افزودن به لیست مطالعه.");
    }
}

// تغییر وضعیت به خوانده‌شده
async function markAsRead(id) {
    const ratingStr = prompt("به این کتاب از ۱ تا ۵ چه امتیازی می‌دهید؟ (اختیاری)");
    const rating = ratingStr ? parseFloat(ratingStr) : null;

    try {
        await fetch(`${API_URL}/books/${id}/status`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: "read", rating })
        });
        loadUserBooks();
    } catch (err) {
        console.error("خطا در بروزرسانی وضعیت:", err);
    }
}

// حذف کتاب
async function deleteBook(id) {
    try {
        await fetch(`${API_URL}/books/${id}`, { method: "DELETE" });
        loadUserBooks();
    } catch (err) {
        console.error("خطا در حذف کتاب:", err);
    }
}

// دریافت پیشنهاد هوشمند از جمنای و نمایش کارت‌ها
recommendBtn.addEventListener("click", async () => {
    const customMood = document.getElementById("custom-mood").value.trim();

    loadingBox.classList.remove("hidden");
    tasteBox.classList.add("hidden");
    recGrid.innerHTML = "";
    recommendBtn.disabled = true;

    try {
        const res = await fetch(`${API_URL}/recommend/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ custom_mood: customMood })
        });

        const data = await res.json();
        lastRecommendedBooks = data.recommendations || [];

        if (data.taste_analysis) {
            tasteText.textContent = data.taste_analysis;
            tasteBox.classList.remove("hidden");
        }

        lastRecommendedBooks.forEach(book => {
            const fallbackCover = createFallbackCover(book.title);
            const coverSrc = book.cover_url || fallbackCover;
            const tagsHtml = (book.vibe_tags || []).map(tag => `<span class="tag">#${tag}</span>`).join("");

            const card = document.createElement("div");
            card.className = "rec-card";
            card.innerHTML = `
                <img src="${coverSrc}" onerror="this.onerror=null; this.src='${fallbackCover}';" alt="${book.title}" class="rec-cover">
                <div class="rec-body">
                    <div>
                        <h3 class="rec-title">${book.title}</h3>
                        <p class="rec-author">اثر ${book.author}</p>
                    </div>
                    <div class="tags">${tagsHtml}</div>
                    
                    <div>
                        <div class="rec-section-title">🎯 چرا این کتاب؟</div>
                        <p class="rec-text">${book.reason}</p>
                    </div>

                    <div>
                        <div class="rec-section-title">📖 تصویر کلی (بدون اسپویل)</div>
                        <p class="rec-text">${book.spoiler_free_summary}</p>
                    </div>

                    <div>
                        <div class="rec-section-title">👤 مناسب برای:</div>
                        <p class="rec-text">${book.target_audience}</p>
                    </div>

                    <button type="button" class="wishlist-add-btn" onclick="addToWishlist('${book.title.replace(/'/g, "\\'")}', '${book.author.replace(/'/g, "\\'")}')">
                        🔖 افزودن به لیست مطالعه
                    </button>
                </div>
            `;
            recGrid.appendChild(card);
        });

    } catch (err) {
        alert("خطا در ارتباط با هوش مصنوعی.");
        console.error(err);
    } finally {
        loadingBox.classList.add("hidden");
        recommendBtn.disabled = false;
    }
});

// چت تعاملی با مشاور کتابخانه
chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;

    appendMessage(message, "user-msg");
    chatInput.value = "";

    const thinkingMsg = document.createElement("div");
    thinkingMsg.className = "msg ai-msg";
    thinkingMsg.textContent = "⏳ در حال بررسی و نوشتن پاسخ...";
    chatMessages.appendChild(thinkingMsg);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const recSummary = lastRecommendedBooks.map(b => `${b.title} اثر ${b.author}`).join("، ");

    try {
        const res = await fetch(`${API_URL}/chat/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                message,
                recent_recommendations: recSummary
            })
        });

        if (!res.ok) {
            throw new Error(`Server error: ${res.status}`);
        }

        const data = await res.json();
        thinkingMsg.textContent = data.reply;
    } catch (err) {
        thinkingMsg.textContent = "❌ خطا در دریافت پاسخ از مشاور. ترمینال سرور را بررسی کنید.";
        console.error(err);
    }
});

function appendMessage(text, className) {
    const div = document.createElement("div");
    div.className = `msg ${className}`;
    div.textContent = text;
    chatMessages.appendChild(div);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

loadUserBooks();