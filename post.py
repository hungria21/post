from telethon import TelegramClient, events
from telethon.tl.types import User, InputPeerUser
from telethon.tl.functions.users import GetFullUserRequest
from langdetect import detect
import os
import re
import asyncio
from config import API_ID, API_HASH, BOT_TOKEN, LANGUAGE_CODES

# Inicializa o cliente
client = TelegramClient('bot_session', API_ID, API_HASH)

# Dicionário para armazenar dados temporários dos usuários
user_data = {}

async def download_profile_photo(username):
    """Função para baixar a foto de perfil do bot"""
    try:
        bot_entity = await client.get_entity(username)
        profile_photo = await client.download_profile_photo(bot_entity, "bot_photo.jpg")
        return profile_photo
    except Exception as e:
        print(f"Erro ao baixar foto: {e}")
        return None

async def get_bot_language(username):
    """Função para detectar o idioma pela bio do bot"""
    try:
        bot_entity = await client.get_entity(username)
        full_bot = await client(GetFullUserRequest(bot_entity.id))
        
        # Verifica se a bio existe e tenta detectar o idioma
        if full_bot.full_user.about:
            try:
                # Tenta detectar o idioma da primeira linha não vazia
                lines = [line.strip() for line in full_bot.full_user.about.split('\n') if line.strip()]
                for line in lines:
                    try:
                        lang_code = detect(line)
                        detected_lang = LANGUAGE_CODES.get(lang_code, None)
                        if detected_lang:
                            return detected_lang
                    except:
                        continue
                return 'desconhecido'
            except:
                return 'desconhecido'
        return 'desconhecido'
    except Exception as e:
        print(f"Erro ao detectar idioma: {e}")
        return 'desconhecido'

async def create_post(bot_username):
    """Função para criar a postagem formatada"""
    try:
        # Remove o @ se presente
        clean_username = bot_username.replace('@', '')
        
        # Obtém informações do bot
        bot_entity = await client.get_entity(bot_username)
        language = await get_bot_language(bot_username)
        
        # Monta a postagem
        post = f"**{bot_entity.first_name}**\n"
        post += "━━━━━━━━━━\n"
        post += f"➧ Username: @{clean_username}\n"
        post += f"➧ Idioma: {language}\n"
        post += f"➧ Grupo:\n"  # Campo em branco para preenchimento manual
        post += f"➧ Tags:\n\n"
        post += f"**ℹ️ Descrição:**\n"
        post += f"\n"  # Descrição em branco
        post += "━━━━━━━━━━\n"
        post += f"**Link:** T.me/{clean_username}"
        
        return post
    except Exception as e:
        print(f"Erro ao criar post: {e}")
        return None

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Manipulador do comando /start"""
    await event.reply("Olá! Envie o username ou link do bot que você quer criar uma postagem.")

@client.on(events.NewMessage(pattern=r'(?i)@?\w+bot$|t\.me/\w+bot$'))
async def bot_username_handler(event):
    """Manipulador para receber username do bot"""
    try:
        username = event.text.strip()
        
        # Extrai username do link se necessário
        if 't.me/' in username:
            username = username.split('/')[-1]
        if not username.startswith('@'):
            username = '@' + username
        
        # Cria a postagem diretamente
        photo_path = await download_profile_photo(username)
        post = await create_post(username)
        
        if post and photo_path:
            await client.send_file(
                event.chat_id,
                file=photo_path,
                caption=post,
                reply_to=event.id,
                parse_mode='md'  # Habilita markdown para o negrito funcionar
            )
            os.remove(photo_path)
        else:
            await event.reply("❌ Não foi possível encontrar esse bot. Verifique se o username está correto e tente novamente.")
    except Exception as e:
        await event.reply("❌ Não foi possível encontrar esse bot. Verifique se o username está correto e tente novamente.")

# Inicia o bot
print("Bot iniciado...")
client.start(bot_token=BOT_TOKEN)
client.run_until_disconnected()