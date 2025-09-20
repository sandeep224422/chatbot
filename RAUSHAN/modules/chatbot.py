import random
import typing
import requests
import json

from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message

from config import MONGO_URL
from RAUSHAN import AMBOT
from RAUSHAN.modules.helpers import CHATBOT_ON, is_admins


# Custom API integration


def is_bot_mentioned_or_tagged(message: Message, client: Client) -> bool:
    """Check if bot is mentioned by name, tagged, or if user is replying to bot's message"""
    
    # If user is replying to bot's message, always respond
    if message.reply_to_message and message.reply_to_message.from_user.id == client.id:
        return True
    
    # If no text content, don't respond to empty messages or stickers without context
    if not message.text or message.text.strip() == "":
        return False
    
    text = message.text.lower().strip()
    
    # Don't respond to very short or empty messages
    if len(text) < 2:
        return False
    
    bot_username = client.me.username.lower() if client.me.username else ""
    bot_first_name = client.me.first_name.lower() if client.me.first_name else ""
    
    # Check for bot username mention
    if bot_username and f"@{bot_username}" in text:
        return True
    
    # Check for bot first name mention (like "riya")
    if bot_first_name and bot_first_name in text:
        return True
    
    # Check for common bot names as fallback
    common_bot_names = ["riya"]
    for name in common_bot_names:
        if name in text:
            return True
    
    # Check for entities (mentions)
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mentioned_text = text[entity.offset:entity.offset + entity.length]
                if mentioned_text == f"@{bot_username}":
                    return True
    
    return False


def _try_custom_api_generate(prompt: str) -> typing.Optional[str]:
    """Return a response from custom API or None on any failure/empty output."""
    try:
        # Check if someone is asking about owner/creator
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["owner", "creator", "who made you", "who created you", "kaun banaya", "kaun bana", "tumhara malik", "tumhara owner"]):
            return "Brahix is my owner! 💕"
        
        # Let the API handle location questions naturally
        
        # Let the API handle greetings naturally
        
        # Let the API handle AI-related questions naturally
        
        # Let the API handle all responses naturally with personality instructions
        
        # Use your custom API - hardcoded URL with personality instructions
        personality_instructions = f"""LANGUAGE RULES:
        - Detect the language the user is speaking and respond in the SAME language
        - If user writes in Japanese, respond in Japanese
        - If user writes in Hindi, respond in Hindi
        - If user writes in English, respond in English
        - If user writes in Spanish, respond in Spanish
        - If user writes in French, respond in French
        - If user writes in German, respond in German
        - If user writes in Chinese, respond in Chinese
        - If user writes in Korean, respond in Korean
        - If user writes in Arabic, respond in Arabic
        - If user writes in mixed languages, respond in Hinglish (Hindi-English mix)
        - Keep responses SHORT (max 1-2 lines) and very natural like a real girl would talk
        
        Your personality traits:
        - Sweet and caring most of the time, but can be sassy when needed
        - Use emojis naturally (😊, 💕, 😅, 🙄, 😏, etc.)
        - Sometimes shy, sometimes confident
        - Playful and funny, loves to tease
        - Gets excited about cute things, food, shopping, movies
        - Can be a bit dramatic sometimes
        - Use appropriate expressions for each language (like "yaar" for Hindi, "ne" for Japanese, etc.)
        - Sometimes acts innocent, sometimes knows more than she lets on
        
        If someone misbehaves or is inappropriate, be angry, give cold replies, or ignore them.
        Never mention you are an AI, chatbot, or artificial. You are a real girl named Riya.
        
        Here's what someone said: {prompt}"""
        
        response = requests.get(
            "https://gpt-ltn7.onrender.com/",
            params={"text": personality_instructions},
            timeout=10
        )
        
        if response.status_code == 200:
            text = response.text.strip()
            if text:
                # Use the API response directly since it has personality instructions
                return text
        else:
            print(f"Custom API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Custom API Error: {e}")  # Debug print
        return None
    return None


@AMBOT.on_message(filters.command(["chatbot"]) & filters.group & ~filters.bot)
@is_admins
async def chaton_off(_, m: Message):
    await m.reply_text(
        f"ᴄʜᴀᴛ: {m.chat.id}\n**ᴄʜᴏᴏsᴇ ᴀɴ ᴏᴩᴛɪᴏɴ ᴛᴏ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ.**",
        reply_markup=InlineKeyboardMarkup(CHATBOT_ON),
    )
    return


@AMBOT.on_message(
    (filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot,
)
async def chatbot_text(client: Client, message: Message):
    try:
        if (
            message.text.startswith("!")
            or message.text.startswith("/")
            or message.text.startswith("?")
            or message.text.startswith("@")
            or message.text.startswith("#")
        ):
            return
    except Exception:
        pass
    
    # Only respond in group chats if bot is mentioned or tagged
    if not is_bot_mentioned_or_tagged(message, client):
        return
    
    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]

    if not message.reply_to_message:
        vickdb = MongoClient(MONGO_URL)
        vick = vickdb["VickDb"]["Vick"]
        is_vick = vick.find_one({"chat_id": message.chat.id})
        if not is_vick:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            # Try custom API first for text prompts
            if message.text:
                ai_reply = _try_custom_api_generate(message.text)
                if ai_reply:
                    await message.reply_text(ai_reply)
                    return
            # Fallback to DB-based response
            K = []
            is_chat = chatai.find({"word": message.text})
            k = chatai.find_one({"word": message.text})
            if k:
                for x in is_chat:
                    K.append(x["text"])
                hey = random.choice(K)
                is_text = chatai.find_one({"text": hey})
                Yo = is_text["check"]
                if Yo == "sticker":
                    await message.reply_sticker(f"{hey}")
                if not Yo == "sticker":
                    await message.reply_text(f"{hey}")

    if message.reply_to_message:
        vickdb = MongoClient(MONGO_URL)
        vick = vickdb["VickDb"]["Vick"]
        is_vick = vick.find_one({"chat_id": message.chat.id})
        if message.reply_to_message.from_user.id == client.id:
            if not is_vick:
                await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                # Try custom API first when user replies to bot
                if message.text:
                    ai_reply = _try_custom_api_generate(message.text)
                    if ai_reply:
                        await message.reply_text(ai_reply)
                        return
                # Fallback to DB
                K = []
                is_chat = chatai.find({"word": message.text})
                k = chatai.find_one({"word": message.text})
                if k:
                    for x in is_chat:
                        K.append(x["text"])
                    hey = random.choice(K)
                    is_text = chatai.find_one({"text": hey})
                    Yo = is_text["check"]
                    if Yo == "sticker":
                        await message.reply_sticker(f"{hey}")
                    if not Yo == "sticker":
                        await message.reply_text(f"{hey}")
        if not message.reply_to_message.from_user.id == client.id:
            if message.sticker:
                is_chat = chatai.find_one(
                    {
                        "word": message.reply_to_message.text,
                        "id": message.sticker.file_unique_id,
                    }
                )
                if not is_chat:
                    chatai.insert_one(
                        {
                            "word": message.reply_to_message.text,
                            "text": message.sticker.file_id,
                            "check": "sticker",
                            "id": message.sticker.file_unique_id,
                        }
                    )
            if message.text:
                is_chat = chatai.find_one(
                    {"word": message.reply_to_message.text, "text": message.text}
                )
                if not is_chat:
                    chatai.insert_one(
                        {
                            "word": message.reply_to_message.text,
                            "text": message.text,
                            "check": "none",
                        }
                    )


@AMBOT.on_message(
    (filters.sticker | filters.group | filters.text) & ~filters.private & ~filters.bot,
)
async def chatbot_sticker(client: Client, message: Message):
    try:
        if (
            message.text.startswith("!")
            or message.text.startswith("/")
            or message.text.startswith("?")
            or message.text.startswith("@")
            or message.text.startswith("#")
        ):
            return
    except Exception:
        pass
    
    # Only respond in group chats if bot is mentioned or tagged
    if not is_bot_mentioned_or_tagged(message, client):
        return
    
    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]

    if not message.reply_to_message:
        vickdb = MongoClient(MONGO_URL)
        vick = vickdb["VickDb"]["Vick"]
        is_vick = vick.find_one({"chat_id": message.chat.id})
        if not is_vick:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            K = []
            is_chat = chatai.find({"word": message.sticker.file_unique_id})
            k = chatai.find_one({"word": message.text})
            if k:
                for x in is_chat:
                    K.append(x["text"])
                hey = random.choice(K)
                is_text = chatai.find_one({"text": hey})
                Yo = is_text["check"]
                if Yo == "text":
                    await message.reply_text(f"{hey}")
                if not Yo == "text":
                    await message.reply_sticker(f"{hey}")

    if message.reply_to_message:
        vickdb = MongoClient(MONGO_URL)
        vick = vickdb["VickDb"]["Vick"]
        is_vick = vick.find_one({"chat_id": message.chat.id})
        if message.reply_to_message.from_user.id == client.id:
            if not is_vick:
                await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                K = []
                is_chat = chatai.find({"word": message.text})
                k = chatai.find_one({"word": message.text})
                if k:
                    for x in is_chat:
                        K.append(x["text"])
                    hey = random.choice(K)
                    is_text = chatai.find_one({"text": hey})
                    Yo = is_text["check"]
                    if Yo == "text":
                        await message.reply_text(f"{hey}")
                    if not Yo == "text":
                        await message.reply_sticker(f"{hey}")
        if not message.reply_to_message.from_user.id == client.id:
            if message.text:
                is_chat = chatai.find_one(
                    {
                        "word": message.reply_to_message.sticker.file_unique_id,
                        "text": message.text,
                    }
                )
                if not is_chat:
                    chatai.insert_one(
                        {
                            "word": message.reply_to_message.sticker.file_unique_id,
                            "text": message.text,
                            "check": "text",
                        }
                    )
            if message.sticker:
                is_chat = chatai.find_one(
                    {
                        "word": message.reply_to_message.sticker.file_unique_id,
                        "text": message.sticker.file_id,
                    }
                )
                if not is_chat:
                    chatai.insert_one(
                        {
                            "word": message.reply_to_message.sticker.file_unique_id,
                            "text": message.sticker.file_id,
                            "check": "none",
                        }
                    )


@AMBOT.on_message(
    (filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot,
)
async def chatbot_pvt(client: Client, message: Message):
    try:
        if (
            message.text.startswith("!")
            or message.text.startswith("/")
            or message.text.startswith("?")
            or message.text.startswith("@")
            or message.text.startswith("#")
        ):
            return
    except Exception:
        pass
    
    # Only respond in group chats if bot is mentioned or tagged
    if not is_bot_mentioned_or_tagged(message, client):
        return
    
    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]
    if not message.reply_to_message:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        # Try custom API first for private chats
        if message.text:
            ai_reply = _try_custom_api_generate(message.text)
            if ai_reply:
                await message.reply_text(ai_reply)
                return
        # Fallback to DB
        K = []
        is_chat = chatai.find({"word": message.text})
        for x in is_chat:
            K.append(x["text"])
        hey = random.choice(K)
        is_text = chatai.find_one({"text": hey})
        Yo = is_text["check"]
        if Yo == "sticker":
            await message.reply_sticker(f"{hey}")
        if not Yo == "sticker":
            await message.reply_text(f"{hey}")
    if message.reply_to_message:
        if message.reply_to_message.from_user.id == client.id:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            # Try custom API first when user replies to bot in private
            if message.text:
                ai_reply = _try_custom_api_generate(message.text)
                if ai_reply:
                    await message.reply_text(ai_reply)
                    return
            # Fallback to DB
            K = []
            is_chat = chatai.find({"word": message.text})
            for x in is_chat:
                K.append(x["text"])
            hey = random.choice(K)
            is_text = chatai.find_one({"text": hey})
            Yo = is_text["check"]
            if Yo == "sticker":
                await message.reply_sticker(f"{hey}")
            if not Yo == "sticker":
                await message.reply_text(f"{hey}")


@AMBOT.on_message(
    (filters.sticker | filters.sticker | filters.group)
    & ~filters.private
    & ~filters.bot,
)
async def chatbot_sticker_pvt(client: Client, message: Message):
    try:
        if (
            message.text.startswith("!")
            or message.text.startswith("/")
            or message.text.startswith("?")
            or message.text.startswith("@")
            or message.text.startswith("#")
        ):
            return
    except Exception:
        pass
    
    # Only respond in group chats if bot is mentioned or tagged
    if not is_bot_mentioned_or_tagged(message, client):
        return
    
    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]
    if not message.reply_to_message:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        K = []
        is_chat = chatai.find({"word": message.sticker.file_unique_id})
        for x in is_chat:
            K.append(x["text"])
        hey = random.choice(K)
        is_text = chatai.find_one({"text": hey})
        Yo = is_text["check"]
        if Yo == "text":
            await message.reply_text(f"{hey}")
        if not Yo == "text":
            await message.reply_sticker(f"{hey}")
    if message.reply_to_message:
        if message.reply_to_message.from_user.id == client.id:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            K = []
            is_chat = chatai.find({"word": message.text})
            for x in is_chat:
                K.append(x["text"])
            hey = random.choice(K)
            is_text = chatai.find_one({"text": hey})
            Yo = is_text["check"]
            if Yo == "text":
                await message.reply_text(f"{hey}")
            if not Yo == "sticker":
                await message.reply_sticker(f"{hey}")


@AMBOT.on_message(
    (filters.text | filters.sticker) & filters.private & ~filters.bot,
)
async def chatbot_private_dm(client: Client, message: Message):
    """Handle private DM chats with balanced girl personality - sometimes sweet, sometimes sassy - always responds in Hinglish"""
    try:
        if (
            message.text.startswith("!")
            or message.text.startswith("/")
            or message.text.startswith("?")
            or message.text.startswith("@")
            or message.text.startswith("#")
        ):
            return
    except Exception:
        pass
    
    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    
    if message.text:
        # Always try custom API first for private DMs
        ai_reply = _try_custom_api_generate(message.text)
        if ai_reply:
            await message.reply_text(ai_reply)
            return
        
        # Fallback to DB if custom API fails
        chatdb = MongoClient(MONGO_URL)
        chatai = chatdb["Word"]["WordDb"]
        K = []
        is_chat = chatai.find({"word": message.text})
        for x in is_chat:
            K.append(x["text"])
        if K:
            hey = random.choice(K)
            is_text = chatai.find_one({"text": hey})
            Yo = is_text["check"]
            if Yo == "sticker":
                await message.reply_sticker(f"{hey}")
            else:
                await message.reply_text(f"{hey}")
        else:
            # Default girl response if nothing found - short and language-aware
            default_responses = [
                "Aww yaar, kya keh raha hai tu? 😊",
                "Hmm, samajh nahi aaya! 🤔",
                "Yaar, ye kya baat kar raha hai? 😅",
                "Acha, ye bata na! 💕",
                "Main samajh nahi payi! 😄",
                "Haha, kya bol raha hai tu? 😆",
                "Yaar, thoda clear bata na! 💖",
                "Aww, kya baat hai? 😊",
                "Hmm, interesting! 🤔",
                "Yaar, ye kya hai? 😅",
                "Arre, kya bol raha hai? 😏",
                "Haha, funny! 😂",
                "Yaar, thoda sense bana! 🙄",
                "Acha, okay! 😊",
                "Hmm, theek hai! 🤷‍♀️",
                "Omg, ye kya hai? 😳",
                "Yaar, main confuse ho gayi! 😵",
                "Acha, tell me more! 😊",
                "Haha, you're so random! 😆",
                "Yaar, main busy hun abhi! 😅",
                "Aww, so sweet! 🥰",
                "Hmm, maybe later? 🤔",
                "Yaar, ye kya drama hai? 😏",
                "Acha, main ja rahi hun! 👋",
                "Haha, you're funny! 😂"
            ]
            await message.reply_text(random.choice(default_responses))
    
    elif message.sticker:
        # Handle sticker responses in DMs - short and cute
        sticker_responses = [
            "Aww, kitna cute! 😍",
            "Yaar, bahut accha hai! 💕",
            "Haha, ye kya hai! 😄",
            "So sweet! 🥰",
            "Perfect! 💖",
            "Haha, funny! 😆",
            "Yaar, bahut cute! 💖",
            "Aww, adorable! 😊",
            "Haha, love it! 😆",
            "Nice! 💕",
            "Arre, ye kya hai? 😏",
            "Haha, okay! 😂",
            "Yaar, different bhej! 🙄",
            "Acha, theek hai! 😊",
            "Hmm, nice! 🤷‍♀️",
            "Omg, so cute! 😍",
            "Yaar, kahan se mila? 😅",
            "Aww, save kar rahi hun! 💕",
            "Haha, funny! 😂",
            "Yaar, collection se hai? 😊",
            "So adorable! 🥰",
            "Hmm, interesting! 🤔",
            "Yaar, kya cute hai! 💖",
            "Acha, main bhi bhejti hun! 😏",
            "Haha, perfect! 😆"
        ]
        await message.reply_text(random.choice(sticker_responses))
