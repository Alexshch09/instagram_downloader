# Telegram Instagram Downloader Bot

A Telegram bot that allows users to download Instagram videos by simply sending a link. The bot leverages RapidAPI for fetching video information and stores user queries in an SQLite database for analytics.

## Features
- Download Instagram videos via RapidAPI.
- User access control via `ALLOWED_USERS`.
- Stores query history in an SQLite database.
- Provides usage statistics for each user.

---

## Getting Started

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Telegram Bot token (from [BotFather](https://core.telegram.org/bots#botfather)).
- RapidAPI key for the Instagram Downloader API.

---

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Alexshch09/instagram_downloader.git
   cd instagram_downloader
   ```

2. Create a .env file:
   ```bash
    BOT_TOKEN=your-telegram-bot-token
    RAPIDAPI_KEY=your-rapidapi-key
    ALLOWED_USERS=12345678,98765432  # Replace with your allowed Telegram user IDs
   ```

3. Build the Docker image:
    ```bash
    docker-compose build
    ```

4. Start the bot service:
    ```bash
    docker-compose up -d
    ```

Example Commands
 - /start: Get a welcome message and instructions.
 - /history: View your query history and stats.

---

Persistent Storage
Query data is stored in an SQLite database in the data directory. Mount this directory when deploying with Docker to retain history.