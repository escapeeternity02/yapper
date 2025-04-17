
import logging
import random
import asyncio
from flask import Flask

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

# Contextual replies
def generate_contextual_reply(text, is_admin=False):
    text = text.lower()
    reply = None

    if "tired" in text:
        reply = "Mood. Sleep schedule’s a myth here."
    elif "who are you" in text or "what are you" in text:
        reply = "Just your friendly yap neighbor."
    elif "lol" in text or "lmao" in text:
        reply = "Literally me 😂"
    elif "bot" in text:
        reply = "You callin' me out? 👀"
    elif "why" in text:
        reply = "Why not?"
    elif "admin" in text:
        reply = "Admins keep this realm in balance fr."

    if is_admin:
        admin_respects = [
            "Respect, boss 🫡", "Big facts, appreciate that", "Noted, thanks legend",
            "Admin wisdom right there 🔥"
        ]
        reply = reply or random.choice(admin_respects)

    return reply or "idk what to say but here I am anyway."

# Health check route to keep the server alive
@app.route('/health', methods=['GET'])
def health_check():
    return "YapperBot is running!", 200

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
            except:
                pass
            break

if __name__ == "__main__":
    # Start Flask server in a separate thread to handle HTTP requests
    import threading
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000)).start()
    
    # Your existing bot logic here (telethon, messaging, etc.)
    asyncio.run(main_bot_logic())
