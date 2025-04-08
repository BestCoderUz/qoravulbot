from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
import re
import time

# === INSERT YOUR VALUES HERE ===
api_id = 29766810           # example: 12345678 (integer, no quotes)
api_hash = '1e4e06c4693b0682c0fc90cc96675f20'      # example: 'abcd1234efgh5678ijkl9012mnop3456'
bot_token = '1817596018:AAEvhSM8EYI-mOBqwTZVC8bDaCoU9yFwhIk'
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Link va username regex
link_pattern = re.compile(
    r'(@\w+|'               
    r'https?://\S+|'        
    r'\b\w+\.(com|uz|net|org|ru|info|biz|io|me)\b)'   
)

# Haqoratli so'zlar ro'yxati
bad_words = [
    "fuck", "bitch", "shit", "asshole", "bastard",
    "сука", "блять", "пизда", "нахуй", "мудак",
    "ahmoq", "sik", "sikish", "yaramas", "kal", "siktir", "it", "harom"
]

# 10 minutga ban qilish funksiyasi
async def mute_user(event, user_id):
    rights = ChatBannedRights(
        until_date=int(time.time()) + 600,  # 10 minut = 600 sekund
        send_messages=True
    )
    try:
        await bot(EditBannedRequest(
            event.chat_id,
            user_id,
            rights
        ))
        print(f"Muted {user_id} for 10 minutes")
    except Exception as e:
        print(f"Failed to mute: {e}")

@bot.on(events.NewMessage)
async def handler(event):
    if event.is_group:
        message_text = event.raw_text.lower()

        # 1. Link yoki haqorat bormi tekshirish
        if link_pattern.search(message_text) or any(bad_word in message_text for bad_word in bad_words):
            try:
                await event.delete()
                await mute_user(event, event.sender_id)
            except Exception as e:
                print(f"Error: {e}")

        # 2. Agar admin /ban komandasini yozsa
        if event.raw_text.lower() == '/ban' and event.is_reply:
            try:
                reply_msg = await event.get_reply_message()
                reply_text = reply_msg.raw_text.lower()

                # Reply qilingan matnni haqoratlar ro'yxatiga qo'shamiz
                bad_words.append(reply_text.strip())

                # Reply bergan foydalanuvchini 10 minutga cheklaymiz
                await mute_user(event, reply_msg.sender_id)

                await event.respond("So'z ro'yxatga qo'shildi va foydalanuvchi 10 minutga cheklangan.")
            except Exception as e:
                print(f"Error in /ban: {e}")

bot.run_until_disconnected()
