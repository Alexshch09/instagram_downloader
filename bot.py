import sqlite3
from datetime import datetime
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os


BOT_TOKEN = os.getenv("BOT_TOKEN")
HEADERS = {
    "x-rapidapi-key": os.getenv("RAPIDAPI_KEY"),
    "x-rapidapi-host": "instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com"
}

API_URL = "https://instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com/get-info-rapidapi"

ALLOWED_USERS = list(map(int, os.getenv("ALLOWED_USERS", "").split(",")))

# Initialize SQLite database
DB_NAME = "data/history.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            query TEXT NOT NULL,
            date TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Save query to the database
def save_query(user_id, username, query):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO queries (user_id, username, query, date)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, query, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# Get query statistics
def get_stats(user_id, page=1, per_page=5):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Total requests
    cursor.execute("SELECT COUNT(*) FROM queries WHERE user_id = ?", (user_id,))
    total_requests = cursor.fetchone()[0]
    
    # Requests this month
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute("SELECT COUNT(*) FROM queries WHERE user_id = ? AND date LIKE ?", (user_id, f"{current_month}%"))
    monthly_requests = cursor.fetchone()[0]

    # Paginated history
    offset = (page - 1) * per_page
    cursor.execute("""
        SELECT id, query, date FROM queries
        WHERE user_id = ?
        ORDER BY date DESC
        LIMIT ? OFFSET ?
    """, (user_id, per_page, offset))
    history = cursor.fetchall()
    
    conn.close()
    return total_requests, monthly_requests, history

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ У вас нет доступа к этому боту.")
        return

    await update.message.reply_text("👋 Привет! Отправьте мне ссылку на Instagram, и я верну вам видео.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    message_text = update.message.text
    chat_id = update.message.chat_id

    # Check user permission
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ У вас нет доступа к этому боту.")
        return

    # Validate the Instagram URL
    if "instagram.com" not in message_text:
        await update.message.reply_text("⚠️ Отправьте действительную ссылку на Instagram.")
        return

    # Save the query
    save_query(user_id, username, message_text)

    # Query the RapidAPI service
    params = {"url": message_text}
    response = requests.get(API_URL, headers=HEADERS, params=params)

    if response.status_code == 200:
        data = response.json()
        video_url = data.get("download_url")

        if video_url:
            # Fetch the video
            video_response = requests.get(video_url, stream=True)
            if video_response.status_code == 200:
                await context.bot.send_video(chat_id=chat_id, video=video_response.content)
            else:
                await context.bot.send_message(chat_id=chat_id, text="❌ Не удалось загрузить видео.")
        else:
            await context.bot.send_message(chat_id=chat_id, text="⚠️ Видео для загрузки не найдено.")
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Ошибка при получении информации о видео. Код: {response.status_code}")

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ У вас нет доступа к этому боту.")
        return

    # Parse page number
    page = 1
    if context.args:
        try:
            page = int(context.args[0])
        except ValueError:
            await update.message.reply_text("⚠️ Укажите корректный номер страницы.")
            return

    total_requests, monthly_requests, history = get_stats(user_id, page)
    
    if not history:
        await update.message.reply_text("📜 История запросов пуста.")
        return

    # Format history
    history_text = "\n".join([f"{row[0]}. {row[1]} ({row[2]})" for row in history])
    response_text = (
        f"📊 Всего запросов: {total_requests}\n"
        f"📅 Запросов за этот месяц: {monthly_requests}\n\n"
        f"📜 История запросов (Страница {page}):\n{history_text}"
    )
    await update.message.reply_text(response_text)

# Main function
def main():
    # Initialize database
    init_db()

    # Replace 'YOUR_BOT_TOKEN' with your Telegram bot token
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot
    print("🤖 Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
