from telethon.sync import TelegramClient
from telethon.tl.types import InputMessageEntityMentionName
import time

api_id = '27165396'
api_hash = 'b5f4ce290449f9cfbe129a25105ac1d9'
client = TelegramClient('session_name', api_id, api_hash)
client.start()

message_template = "Привет! Мы разработчики сайтов под ключ. Пишите!"

def send_hidden_mentions(chat_id, participants, chunk_size=5):
    for i in range(0, len(participants), chunk_size):
        mention_chunk = participants[i:i + chunk_size]
        entities = []
        for p in mention_chunk:
            if p.username:
                entities.append(InputMessageEntityMentionName(offset=0, length=1, user_id=p.id))
        
        client.send_message(
            chat_id,
            message_template,
            entities=entities
        )
        time.sleep(600)

chat_id = -1001967254470  # ID группы
participants = client.get_participants(chat_id)

send_hidden_mentions(chat_id, participants)