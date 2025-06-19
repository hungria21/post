from telethon import TelegramClient, events
from telethon.tl.types import User, InputPeerUser
from telethon.tl.functions.users import GetFullUserRequest
from langdetect import detect
import os
import re
import asyncio
import sys
from config import API_ID, API_HASH, BOT_TOKEN, LANGUAGE_CODES

# Startup check for API credentials
if not all([API_ID, API_HASH, BOT_TOKEN]):
    error_message = """
    ################################################################################
    ERROR: Missing API Credentials
    ################################################################################

    Telegram API_ID, API_HASH, or BOT_TOKEN is not configured.

    Please ensure these are set as environment variables (recommended)
    or directly in the config.py file.

    For guidance, refer to the config.py.example file.

    Example using environment variables:
        export TELEGRAM_API_ID="your_api_id"
        export TELEGRAM_API_HASH="your_api_hash"
        export TELEGRAM_BOT_TOKEN="your_bot_token"

    To set them directly in config.py (less recommended for security reasons,
    ensure config.py is in .gitignore if you do this):
        API_ID = 'your_api_id_here'
        API_HASH = 'your_api_hash_here'
        BOT_TOKEN = 'your_bot_token_here'
    ################################################################################
    """
    print(error_message)
    sys.exit(1)
else:
    print("Configuration loaded successfully.")

# Inicializa o cliente
client = TelegramClient('bot_session', API_ID, API_HASH)

# Dicionário para armazenar dados temporários dos usuários
# Key: chat_id
# Value: dictionary with state, e.g., {'stage': 'awaiting_language', 'username': 'bot_user', 'photo_path': 'path/to/photo.jpg',
# 'language': 'lang', 'group': 'group_name', 'original_message_id': event.id}
user_data = {}

async def download_profile_photo(username):
    """Função para baixar a foto de perfil do bot"""
    try:
        bot_entity = await client.get_entity(username)
        if not bot_entity:
            return None, "Error: Bot entity not found."
        profile_photo = await client.download_profile_photo(bot_entity, "bot_photo.jpg")
        if profile_photo is None:
            return None, "Error: Bot has no profile photo or it could not be downloaded."
        return profile_photo, None
    except ValueError:
        return None, f"Error: Invalid username format for '{username}'."
    except Exception as e:
        return None, f"Error downloading photo: An unexpected error occurred."

async def get_bot_language(username):
    """Função para detectar o idioma pela bio do bot"""
    try:
        bot_entity = await client.get_entity(username)
        if not bot_entity:
             return None, "Error: Bot entity not found (unexpected)."
        full_bot = await client(GetFullUserRequest(bot_entity.id))
        if full_bot.full_user.about:
            lines = [line.strip() for line in full_bot.full_user.about.split('\n') if line.strip()]
            for line in lines:
                try:
                    lang_code = detect(line)
                    detected_lang = LANGUAGE_CODES.get(lang_code, None)
                    if detected_lang:
                        return detected_lang, None
                except Exception:
                    continue
            return 'desconhecido', None
        return 'desconhecido', None
    except ValueError:
        return None, f"Error: Bot username '{username}' is invalid or the bot does not exist."
    except Exception as e:
        return None, "Error: Could not access bot details or bio (possibly a network issue or bot restrictions)."

async def create_post(bot_username, language, group, description):
    """Função para criar a postagem formatada com todos os detalhes fornecidos."""
    try:
        clean_username = bot_username.replace('@', '')
        bot_entity = await client.get_entity(bot_username)
        if not bot_entity or not bot_entity.first_name:
            return None, "Error: Could not retrieve bot's first name."

        post = f"**{bot_entity.first_name}**\n"
        post += "━━━━━━━━━━\n"
        post += f"➧ Username: @{clean_username}\n"
        post += f"➧ Idioma: {language}\n"
        post += f"➧ Grupo: {group}\n"
        post += f"➧ Tags:\n\n"
        post += f"**ℹ️ Descrição:**\n{description}\n"
        post += "━━━━━━━━━━\n"
        post += f"**Link:** T.me/{clean_username}"
        return post, None
    except ValueError:
        return None, f"Error: Bot username '{bot_username}' seems invalid or the bot does not exist."
    except Exception as e:
        return None, f"Error creating post: An unexpected error occurred."

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    user_data.pop(event.chat_id, None) # Clear any stale state on /start
    await event.reply("Olá! Envie o username ou link do bot que você quer criar uma postagem.")

@client.on(events.NewMessage)
async def description_input_handler(event):
    chat_id = event.chat_id
    if chat_id in user_data and user_data[chat_id].get('stage') == 'awaiting_description':
        current_user_data = user_data[chat_id]
        username = current_user_data['username']
        photo_path = current_user_data['photo_path']
        language = current_user_data['language']
        group = current_user_data['group']
        original_message_id = current_user_data.get('original_message_id')

        description_input = event.text.strip()

        del user_data[chat_id] # Clean up state

        post_content, post_err = await create_post(username, language, group, description_input)

        if post_err or not post_content:
            error_msg = post_err or "Failed to create post with the provided details."
            await event.reply(error_msg)
            if photo_path and os.path.exists(photo_path):
                try: os.remove(photo_path)
                except OSError as e: print(f"Error removing photo_path {photo_path}: {e}")
            raise events.StopPropagation

        reply_to_msg_id = original_message_id or event.id

        if photo_path:
            try:
                await client.send_file(
                    chat_id,
                    file=photo_path,
                    caption=post_content,
                    reply_to=reply_to_msg_id,
                    parse_mode='md'
                )
            except Exception as send_err:
                await event.reply("Error: Could not send the post. Please try again later.")
            finally:
                if os.path.exists(photo_path):
                    try: os.remove(photo_path)
                    except OSError as e: print(f"Error removing photo_path {photo_path}: {e}")
        else: # Fallback if no photo_path, though current flow ensures it.
             await event.reply(post_content, reply_to=reply_to_msg_id)

        raise events.StopPropagation

@client.on(events.NewMessage)
async def group_input_handler(event):
    chat_id = event.chat_id
    if chat_id in user_data and user_data[chat_id].get('stage') == 'awaiting_group':
        current_user_data = user_data[chat_id]
        username = current_user_data['username']
        language = current_user_data['language']
        # photo_path and original_message_id remain in user_data for the next stage

        group_input = event.text.strip()

        user_data[chat_id].update({
            'stage': 'awaiting_description',
            'group': group_input
        })

        await event.reply(
            f"📝 Bot: @{username}\n"
            f"🗣️ Language: {language}\n"
            f"👥 Group: {group_input}\n\n"
            f"What is the **Description** for this bot?",
            parse_mode='md'
        )
        raise events.StopPropagation

@client.on(events.NewMessage)
async def language_input_handler(event):
    chat_id = event.chat_id
    if chat_id in user_data and user_data[chat_id].get('stage') == 'awaiting_language':
        user_supplied_language = event.text.strip()

        current_user_data = user_data[chat_id]
        username = current_user_data['username']
        # photo_path and original_message_id remain

        user_data[chat_id].update({
            'stage': 'awaiting_group',
            'language': user_supplied_language
        })

        await event.reply(
            f"📝 Bot: @{username}\n"
            f"🗣️ Language: {user_supplied_language}\n\n"
            f"What is the **Group** for this bot?",
            parse_mode='md'
        )
        raise events.StopPropagation

@client.on(events.NewMessage(pattern=r'(?i)@?\w+bot$|t\.me/\w+bot$'))
async def bot_username_handler(event):
    chat_id = event.chat_id
    user_data.pop(chat_id, None) # Clear any stale state for this chat
    original_message_id = event.id

    try:
        username = event.text.strip()
        if 't.me/' in username:
            username = username.split('/')[-1]
        if not username.startswith('@'):
            username = '@' + username
        
        photo_path, photo_err = await download_profile_photo(username)
        if photo_err:
            await event.reply(photo_err)
            return
        if not photo_path:
            await event.reply("Error: Failed to download profile photo, reason unknown.")
            return

        language, lang_err = await get_bot_language(username)

        if lang_err:
            await event.reply(lang_err)
            if photo_path and os.path.exists(photo_path): os.remove(photo_path)
            return
        
        current_user_state = {
            'username': username,
            'photo_path': photo_path,
            'original_message_id': original_message_id
        }

        if language == 'desconhecido':
            current_user_state['stage'] = 'awaiting_language'
            user_data[chat_id] = current_user_state
            await event.reply(f"Language for @{username} could not be automatically detected. Please reply with the language of this bot (e.g., Português, Inglês).")
        else:
            current_user_state['stage'] = 'awaiting_group'
            current_user_state['language'] = language
            user_data[chat_id] = current_user_state
            await event.reply(
                f"📝 Bot: @{username}\n"
                f"🗣️ Language: {language}\n\n"
                f"What is the **Group** for this bot?",
                parse_mode='md'
            )
    except Exception as e:
        await event.reply("❌ An unexpected error occurred. Please try again.")

# Inicia o bot
print("Bot iniciado...")
client.start(bot_token=BOT_TOKEN)
client.run_until_disconnected()