import logging
import random
import asyncio
from flask import Flask
from telethon import TelegramClient
import threading
import os
import time

# Flask setup for web service
app = Flask(__name__)

# Setting up logging
logging.basicConfig(filename='yapper_log.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Function to log messages
def log_message(message, sender_id=None, is_reply=False):
    if sender_id:
        logging.info(f"Sent to {sender_id}: {message}")
    else:
        logging.info(f"Sent message: {message}")
        
    if is_reply:
        logging.info(f"Reply message: {message}")

# Memory system (simple)
memory = []

def add_to_memory(line):
    memory.append(line)
    if len(memory) > 30:
        memory.pop(0)

def reference_memory():
    if memory and random.random() < 0.3:
        ref = random.choice(memory)
        return f"Like I said earlier: {ref}"
    return None

# Enhanced Contextual replies with better diversity
def generate_contextual_reply(text, is_admin=False):
    text = text.lower()
    reply = None

    # Enhanced responses with more variety
    if "tired" in text:
        reply = random.choice([
            "Mood. Sleep schedule’s a myth here.",
            "Same, I think I need a nap.",
            "I feel you. It's like the sleep cycle doesn't exist."
        ])
    elif "who are you" in text or "what are you" in text:
        reply = random.choice([
            "Just your friendly yap neighbor.",
            "I'm just a bot trying to fit in. 😎",
            "You can call me Yapper, your chatbot friend."
        ])
    elif "lol" in text or "lmao" in text:
        reply = random.choice([
            "Literally me 😂",
            "I died at that one 😂",
            "That made me laugh, no cap 😂"
        ])
    elif "bot" in text:
        reply = random.choice([
            "You callin' me out? 👀",
            "Yes, I am a bot, but don't judge me! 😅",
            "Yes, I may be a bot, but I’ve got personality!"
        ])
    elif "why" in text:
        reply = random.choice([
            "Why not?",
            "Because... reasons! 🤷‍♂️",
            "Just because, that's why. 😜"
        ])
    elif "admin" in text:
        reply = random.choice([
            "Admins keep this realm in balance fr.",
            "Shoutout to the admins for keeping things running.",
            "Admins are the true heroes here. 🔥"
        ])

    if is_admin:
        admin_respects = [
            "Respect, boss 🫡", "Big facts, appreciate that", "Noted, thanks legend",
            "Admin wisdom right there 🔥"
        ]
        reply = reply or random.choice(admin_respects)

    return reply or random.choice([
        "idk what to say but here I am anyway.",
        "I'm just here vibing, can't relate tho.",
        "Your guess is as good as mine! 😅"
    ])

# Health check route to keep the server alive
@app.route('/health', methods=['GET'])
def health_check():
    return "YapperBot is running!", 200

# Telegram Client setup using API credentials (API ID and API Hash)
api_id = '27161962'  # Replace with your actual API ID
api_hash = 'd1fbc0d985163be463ef2083ffb7b86f'  # Replace with your actual API Hash
session_file_path = os.path.join('sessions', 'session1.session')  # Adjust the session file path

client = TelegramClient(session_file_path, api_id, api_hash)  # API credentials needed

# Admin user IDs for admin-specific replies (adjust with actual admin IDs)
admins = [123456789, 987654321]  # Replace with actual admin user IDs

# Group username
group_username = '@yapplytesting'

# Fake typing simulation function
async def fake_typing(group):
    # Simulate typing for a little delay (mimicking user behavior)
    await asyncio.sleep(random.uniform(1, 3))

# Send message function
async def send_message(group):
    message = "I am just a bot yapping away..."
    await fake_typing(group)
    await client.send_message(group, message)
    log_message(message)

# Time tracking and message limit variables
last_sent_time = time.time()  # Tracks the last message sent
message_count = 0  # Tracks how many messages were sent in the last minute

# Replying function with message limit check
async def reply_to_message(group):
    global last_sent_time, message_count

    # Check if 1 minute has passed since the last message
    if time.time() - last_sent_time > 60:
        message_count = 0  # Reset count after 1 minute

    # Check if the bot has sent less than 3 messages in the last minute
    if message_count < 3:
        async for msg in client.iter_messages(group, limit=50):
            if msg.sender_id and msg.text and random.random() < 0.5:
                is_admin = msg.sender_id in admins
                reply = generate_contextual_reply(msg.text, is_admin)
                memory_reply = reference_memory()

                if memory_reply and random.random() < 0.3:
                    reply = memory_reply

                await fake_typing(group)

                try:
                    await client.send_message(group, reply, reply_to=msg.id)
                    add_to_memory(reply)
                    log_message(reply, msg.sender_id, is_reply=True)

                    # Update time and count after sending a message
                    last_sent_time = time.time()
                    message_count += 1
                except Exception as e:
                    logging.error(f"Error sending message: {e}")
                break
    else:
        # If 3 messages have been sent in the last minute, wait for a while
        logging.info("Message limit reached. Waiting for the next minute.")
        await asyncio.sleep(60 - (time.time() - last_sent_time))  # Wait for the remainder of the minute

# Main bot logic function
async def main_bot_logic():
    await client.start()
    while True:
        await reply_to_message(group_username)
        await asyncio.sleep(1)  # Sleep to avoid hitting API too frequently

# Start Flask server in a separate thread to handle HTTP requests
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    
    # Run the bot logic
    asyncio.run(main_bot_logic())
