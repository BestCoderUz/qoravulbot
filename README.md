from telethon import TelegramClient, events
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
import re
import time

# O'zing ma'lumotlaringni kiriting
api_id = 1234567
api_hash = 'your_api_hash_here'
bot_token = 'your_bot_token_here'

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
        until_date=int(time.time()) + 600,  # 10 minut
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

        # Agar link (reklama) bo'lsa
        if link_pattern.search(message_text):
            try:
                await event.delete()
                await event.respond("⚠️ Reklama tarqatish taqiqlangan!")
            except Exception as e:
                print(f"Error deleting ad: {e}")

        # Agar haqorat (so'kinish) bo'lsa
        elif any(bad_word in message_text for bad_word in bad_words):
            try:
                await event.delete()
                await mute_user(event, event.sender_id)
                await event.respond(f"⚠️ Sökinish taqiqlangan!\n{(await event.get_sender()).first_name} 10 minutga cheklab qo‘yildi.")
            except Exception as e:
                print(f"Error muting user: {e}")

        # Agar admin /ban jo'natsa
        if event.raw_text.lower() == '/ban' and event.is_reply:
            try:
                reply_msg = await event.get_reply_message()
                reply_text = reply_msg.raw_text.lower()

                bad_words.append(reply_text.strip())
                await mute_user(event, reply_msg.sender_id)

                await event.respond("⚠️ So'z ro'yxatga qo'shildi va foydalanuvchi 10 minutga cheklab qo‘yildi.")
            except Exception as e:
                print(f"Error in /ban: {e}")

bot.run_until_disconnected()
