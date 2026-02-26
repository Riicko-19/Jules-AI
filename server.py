import os
import logging
import asyncio
import subprocess
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from dotenv import load_dotenv

# ADK and GenAI imports
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part, Blob

# Import our agents
from agents.manager import MANAGER_AGENT

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Environment Variables
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# WhatsApp API URL
API_URL = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"

# Global session service (in-memory)
session_service = InMemorySessionService()

@app.get("/webhook")
async def verify_webhook(request: Request):
    """Verifies the webhook for WhatsApp."""
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if token == WHATSAPP_TOKEN:
        return PlainTextResponse(content=challenge)
    raise HTTPException(status_code=403, detail="Invalid verify token")

@app.post("/webhook")
async def webhook(request: Request):
    """Handles incoming WhatsApp messages."""
    try:
        data = await request.json()
        logger.info(f"Received webhook: {data}")

        # Check for messages
        entry = data.get("entry", [])
        if not entry:
            return {"status": "ok"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "ok"}

        value = changes[0].get("value", {})
        if "messages" not in value:
            return {"status": "ok"}

        message = value["messages"][0]
        msg_type = message.get("type")
        from_number = message.get("from")

        # Session IDs
        user_id = from_number
        session_id = f"session_{from_number}"

        content = None

        if msg_type == "text":
            text_body = message["text"]["body"]
            content = Content(role="user", parts=[Part(text=text_body)])

        elif msg_type == "audio":
            audio_id = message["audio"]["id"]

            # Download and convert audio
            audio_path = await download_audio(audio_id)
            if audio_path:
                converted_path = await convert_audio(audio_path)

                if converted_path:
                    # Read audio data
                    with open(converted_path, "rb") as f:
                        audio_data = f.read()

                    # Create Content with audio blob
                    # Assuming MP3 format after conversion
                    content = Content(
                        role="user",
                        parts=[
                            Part(inline_data=Blob(mime_type="audio/mp3", data=audio_data)),
                            Part(text="Please listen to this audio and respond.")
                        ]
                    )

                    # Cleanup
                    try:
                        if os.path.exists(audio_path):
                            os.remove(audio_path)
                        if os.path.exists(converted_path):
                            os.remove(converted_path)
                    except Exception as cleanup_error:
                        logger.warning(f"Cleanup error: {cleanup_error}")

        if content:
            # Initialize Runner
            runner = Runner(
                agent=MANAGER_AGENT,
                app_name="whatsapp_assistant",
                session_service=session_service,
                auto_create_session=True
            )

            response_text = ""
            logger.info(f"Running agent for user {user_id}...")

            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                # Check for content in event
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text

            logger.info(f"Agent response: {response_text}")

            if response_text:
                await send_whatsapp_message(from_number, response_text)

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        import traceback
        traceback.print_exc()

    return {"status": "ok"}

async def download_audio(media_id: str) -> str:
    """Downloads audio from WhatsApp."""
    try:
        url = f"https://graph.facebook.com/v19.0/{media_id}"
        headers = {"Authorization": f"Bearer {WHATSAPP_TOKEN}"}

        async with httpx.AsyncClient() as client:
            # Get Media URL
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                 logger.error(f"Failed to get media info: {response.text}")
                 return None

            media_url = response.json().get("url")

            # Download Media
            # Note: Media URL might require Authorization header as well, usually the same one.
            response = await client.get(media_url, headers=headers)
            if response.status_code != 200:
                 logger.error(f"Failed to download media: {response.text}")
                 return None

            filename = f"{media_id}.ogg"
            with open(filename, "wb") as f:
                f.write(response.content)

            return filename
    except Exception as e:
        logger.error(f"Error in download_audio: {e}")
        return None

async def convert_audio(input_path: str) -> str:
    """Converts audio to MP3 using ffmpeg."""
    output_path = input_path.replace(".ogg", ".mp3")
    try:
        # Check if ffmpeg is available
        process = await asyncio.create_subprocess_exec(
            'ffmpeg', '-i', input_path, '-y', output_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            logger.error(f"ffmpeg conversion failed: {stderr.decode()}")
            return None

        return output_path
    except Exception as e:
        logger.error(f"Error converting audio: {e}")
        return None

async def send_whatsapp_message(to: str, text: str):
    """Sends a text message via WhatsApp API."""
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, headers=headers, json=payload)
            logger.info(f"Sent message to {to}, status: {response.status_code}")
            if response.status_code not in [200, 201]:
                logger.error(f"Response body: {response.text}")
    except Exception as e:
        logger.error(f"Error sending message: {e}")
