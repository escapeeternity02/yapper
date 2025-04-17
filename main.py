import logging
import random
import asyncio
from flask import Flask
from telethon import TelegramClient
import threading
import re

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

# Improved keyword matching using regular expressions
def match_keywords(text):
    text = text.lower()

    if re.search(r'\btired\b|\bexhausted\b', text):
        return "Mood. Sleep schedule’s a myth here."
    elif re.search(r'\bwho are you\b|\bwhat are you\b', text):
        return "Just your friendly yap neighbor."
    elif re.search(r'\blol\b|\blmao\b', text):
        return "Literally me 😂"
    elif re.search(r'\bbot\b', text):
        return "You callin' me out? 👀"
    elif re.search(r'\bwhy\b', text):
        return "Why not?"
    elif re.search(r'\badmin\b', text):
        return "Admins keep this realm in balance fr."
    
    return None  # If no match, return None

# Contextual replies
def generate_contextual_reply(text, is_admin=False):
    reply = match_keywords(text)

    if reply:  # If a keyword match was found
        return reply
    else:
        # If no keyword match, provide a fallback response
        return "I’m just vibing here, don’t mind me! 😅"

# Health check route to keep the server alive
@app.route('/health', methods=['GET'])
def health_check():
    return "YapperBot is running!", 200

# Telegram Client setup using session file
client = TelegramClient('session1.session', api_id=None, api_hash=None)  # Using session file directly

# Admin user IDs for admin specific replies (adjust with actual admin IDs)
admins = [123456789, 8050338012]  # Replace with actual admin user IDs

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

# Replying function
async def reply_to_message(group):
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
            except Exception as e:
                logging.error(f"Error sending message: {e}")
            break

# Main bot logic function
async def main_bot_logic():
    await client.start()
    while True:
        await reply_to_message(group_username)
        await asyncio.sleep(20)  # Adjusted to prevent constant spamming

# Start Flask server in a separate thread to handle HTTP requests
if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    
    # Run the bot logic
    asyncio.run(main_bot_logic())
