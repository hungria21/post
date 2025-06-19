# Telegram Bot Post Assistant

## Introduction
The Telegram Bot Post Assistant is a Python script that helps you create formatted posts for Telegram channels or groups, detailing information about other Telegram bots. It fetches the bot's name, profile picture, and language, then interactively prompts you for a group and description to include in the post.

## Features
*   **Automatic Bot Information:** Fetches the bot's display name.
*   **Profile Photo Download:** Downloads the target bot's profile picture to include in the post.
*   **Language Detection:** Attempts to automatically detect the bot's language from its bio.
*   **Interactive Language Input:** If automatic detection fails, it asks you to provide the language.
*   **Interactive Group Input:** Prompts you to specify a 'Group' for the bot.
*   **Interactive Description Input:** Prompts you to provide a 'Description' for the bot.
*   **Formatted Post:** Generates a Markdown-formatted post ready for Telegram.

## Setup Instructions

### Prerequisites
*   Python 3.7 or higher is recommended.

### Dependencies
The script relies on the following Python libraries:
*   `telethon`: For interacting with the Telegram API.
*   `langdetect`: For automatic language detection from the bot's bio.

You can install them using pip:
```bash
pip install telethon langdetect
```

### API Credentials
To use this script, you need three pieces of information:

1.  **`API_ID` and `API_HASH`**: These are your personal Telegram API credentials, associated with your own Telegram account. They allow the script to connect to Telegram as a user to fetch information about other bots (like their bio and profile picture).
    *   **How to obtain**: Go to [my.telegram.org](https://my.telegram.org), log in with your phone number, and click on "API development tools".

2.  **`BOT_TOKEN`**: This is the token for *your* bot that will be running this script and interacting with you to create posts.
    *   **How to obtain**: Talk to [BotFather](https://t.me/BotFather) on Telegram. Use the `/newbot` command and follow the instructions. BotFather will give you a token.

### Configuration
You need to make your `API_ID`, `API_HASH`, and `BOT_TOKEN` available to the script. There are two ways to do this:

**1. Environment Variables (Recommended)**
Set the following environment variables in your system:
```bash
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
export TELEGRAM_BOT_TOKEN="your_bot_token"
```
Replace `"your_api_id"`, `"your_api_hash"`, and `"your_bot_token"` with your actual credentials. The script will automatically read these.

**2. `config.py` File (Alternative)**
*   Copy the `config.py.example` file to a new file named `config.py` in the same directory.
*   Open `config.py` and fill in your credentials:
    ```python
    API_ID = 'your_api_id_here'
    API_HASH = 'your_api_hash_here'
    BOT_TOKEN = 'your_bot_token_here'
    ```
*   **Important**: If you use this method, make sure to add `config.py` to your `.gitignore` file to prevent accidentally committing your credentials to version control.
    ```
    # .gitignore
    config.py
    bot_session.session
    *.jpg
    ```
    (It's also good practice to ignore session files and downloaded images).

## Running the Bot
Once you have configured your credentials, you can run the bot using:
```bash
python post.py
```
You should see a "Bot iniciado..." message if it starts correctly.

## Usage
1.  **Start a conversation with your bot** on Telegram.
2.  Send the `/start` command. The bot will reply with a welcome message.
3.  **Submit a bot's username** (e.g., `@some_bot`) or a link to its profile (e.g., `t.me/some_bot`).
4.  **Conversational Flow:**
    *   **Language:** If the bot's language cannot be detected from its bio, you will be prompted to enter it (e.g., "Português", "English").
    *   **Group:** You will be asked to provide a "Group" for the bot. This is a category or collection name you define.
    *   **Description:** You will be asked to provide a "Description" for the bot.
5.  **Output:** After you provide all the information, the bot will send a message containing the target bot's profile picture and the formatted post, ready to be forwarded or copied.

## Troubleshooting
*   **Missing Credentials Error on Startup:** If the bot prints an error message about missing API credentials and exits, ensure you have configured `API_ID`, `API_HASH`, and `BOT_TOKEN` correctly using either environment variables or the `config.py` file.
*   **"Could not find the bot" errors:** Double-check the spelling of the bot's username or link. Some bots may also have restrictions that prevent information fetching.
*   **Language Detection:** Language detection is based on the bot's bio. If the bio is empty, very short, or in a language not well-supported by `langdetect`, you will be prompted for manual input.
