import random
import typing
import requests
import json

from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from pyrogram.types import InlineKeyboardMarkup, Message

from config import MONGO_URL, OPENAI_API_KEY
from RAUSHAN import AMBOT
from RAUSHAN.modules.helpers import CHATBOT_ON, is_admins


# OpenRouter API key is configured in the function when needed


def _try_openai_generate(prompt: str) -> typing.Optional[str]:
    """Return an OpenRouter response text or None on any failure/empty output."""
    if not OPENAI_API_KEY:
        return None
    try:
        # Check if someone is asking about owner/creator
        prompt_lower = prompt.lower()
        if any(word in prompt_lower for word in ["owner", "creator", "who made you", "who created you", "kaun banaya", "kaun bana", "tumhara malik", "tumhara owner"]):
            return "Brahix is my owner! 💕"
        
        # Check for misbehavior/inappropriate messages
        misbehavior_words = [
            "fuck", "bitch", "slut", "whore", "asshole", "bastard", "idiot", "stupid", "dumb",
            "madarchod", "behenchod", "chutiya", "gandu", "bhosdike", "randi", "kutiya",
            "sex", "fuck you", "fuck off", "go to hell", "die", "kill yourself",
            "hate you", "you suck", "you're ugly", "you're fat", "you're stupid",
            "nude", "naked", "boobs", "ass", "dick", "pussy", "horny", "sexy",
            "marry me", "love you", "kiss", "hug", "touch", "come to me"
        ]
        
        if any(word in prompt_lower for word in misbehavior_words):
            angry_responses = [
                "Arre, kya bakwaas kar raha hai tu? 😠",
                "Yaar, thoda respect kar! 🙄",
                "Hmm, theek hai. Main ignore kar rahi hun! 😒",
                "Acha, bye! 👋",
                "Yaar, ye kya baat hai? 😤",
                "Main baat nahi kar rahi ab! 😑",
                "Thoda decent reh! 😏",
                "Hmm, whatever! 🤷‍♀️",
                "Yaar, grow up! 🙄",
                "Acha, main chali! 😒",
                "Eww, disgusting! 🤢",
                "Yaar, ye kya hai? 😡",
                "Main block kar dungi! 😤",
                "Thoda class maintain kar! 😒",
                "Yaar, main serious hun! 😠",
                "Acha, main ja rahi hun! 😑",
                "Ye sab mat kar! 🙅‍♀️",
                "Yaar, thoda mature ho! 😏",
                "Main upset ho gayi! 😔",
                "Acha, enough! 😤"
            ]
            return random.choice(angry_responses)
        
        # Create balanced girl personality prompt - sometimes sweet, sometimes a bit rude
        girl_prompt = f"""You are a real girl with a balanced personality. Always respond ONLY in Hinglish (Hindi-English mix) no matter what language the user speaks. 
        Keep responses SHORT (max 1-2 lines) and natural. Sometimes be sweet and caring, sometimes be a bit rude or sassy - but not too extreme in either direction.
        Be playful, funny, and have attitude. If someone misbehaves or is inappropriate, be angry or give cold replies.
        Act like a real person - never mention you are an AI, chatbot, or artificial. You are a real girl.
        Support all languages but always reply in Hinglish. Here's what someone said: {prompt}"""
        
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a real girl with balanced personality who always responds in Hinglish. If someone misbehaves, be angry or give cold replies."
                    },
                    {
                        "role": "user",
                        "content": girl_prompt
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7
            })
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result["choices"][0]["message"]["content"].strip()
            if text:
                # If response is too long, truncate it
                if len(text) > 200:
                    text = text[:200] + "..."
                return text
        else:
            print(f"OpenRouter API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"OpenRouter API Error: {e}")  # Debug print
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
    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]

    if not message.reply_to_message:
        vickdb = MongoClient(MONGO_URL)
        vick = vickdb["VickDb"]["Vick"]
        is_vick = vick.find_one({"chat_id": message.chat.id})
        if not is_vick:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            # Try OpenAI first for text prompts
            if message.text:
                ai_reply = _try_openai_generate(message.text)
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
                # Try OpenAI first when user replies to bot
                if message.text:
                    ai_reply = _try_openai_generate(message.text)
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
    chatdb = MongoClient(MONGO_URL)
    chatai = chatdb["Word"]["WordDb"]
    if not message.reply_to_message:
        await client.send_chat_action(message.chat.id, ChatAction.TYPING)
        # Try OpenAI first for private chats
        if message.text:
            ai_reply = _try_openai_generate(message.text)
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
            # Try OpenAI first when user replies to bot in private
            if message.text:
                ai_reply = _try_openai_generate(message.text)
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
        # Always try OpenAI first for private DMs
        ai_reply = _try_openai_generate(message.text)
        if ai_reply:
            await message.reply_text(ai_reply)
            return
        
        # Fallback to DB if OpenAI fails
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
            # Default girl response if nothing found - mix of sweet and sassy
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
                "Hmm, theek hai! 🤷‍♀️"
            ]
            await message.reply_text(random.choice(default_responses))
    
    elif message.sticker:
        # Handle sticker responses in DMs - mix of sweet and sassy
        sticker_responses = [
            "Aww, kitna cute sticker hai! 😍",
            "Yaar, ye sticker bahut accha hai! 💕",
            "Haha, ye kya bheja hai tu! 😄",
            "So sweet! 🥰",
            "Ye sticker perfect hai! 💖",
            "Haha, so funny! 😆",
            "Yaar, ye bahut cute hai! 💖",
            "Aww, so adorable! 😊",
            "Haha, love it! 😆",
            "Ye bahut nice hai! 💕",
            "Arre, ye kya hai? 😏",
            "Haha, okay okay! 😂",
            "Yaar, thoda different bhej! 🙄",
            "Acha, theek hai! 😊",
            "Hmm, nice! 🤷‍♀️"
        ]
        await message.reply_text(random.choice(sticker_responses))
