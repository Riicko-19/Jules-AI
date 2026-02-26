import os
import logging
import asyncio
import subprocess
import tempfile
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
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
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Global session service (in-memory)
session_service = InMemorySessionService()

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming text messages."""
    user_id = str(update.effective_user.id)
    session_id = f"session_{user_id}"
    text_body = update.message.text

    logger.info(f"Received text message from {user_id}: {text_body}")

    content = Content(role="user", parts=[Part(text=text_body)])
    await process_agent_request(update, content, user_id, session_id)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming voice messages."""
    user_id = str(update.effective_user.id)
    session_id = f"session_{user_id}"

    logger.info(f"Received voice message from {user_id}")

    voice_file = await context.bot.get_file(update.message.voice.file_id)

    # Create temporary files for processing
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_ogg:
        ogg_path = temp_ogg.name

    await voice_file.download_to_drive(ogg_path)

    mp3_path = await convert_audio(ogg_path)

    if mp3_path:
        try:
            with open(mp3_path, "rb") as f:
                audio_data = f.read()

            content = Content(
                role="user",
                parts=[
                    Part(inline_data=Blob(mime_type="audio/mp3", data=audio_data)),
                    Part(text="Please listen to this audio and respond.")
                ]
            )

            await process_agent_request(update, content, user_id, session_id)

        except Exception as e:
            logger.error(f"Error processing audio file: {e}")
            await update.message.reply_text("Sorry, I encountered an error processing your voice message.")
        finally:
            # Cleanup
            try:
                if os.path.exists(ogg_path):
                    os.remove(ogg_path)
                if os.path.exists(mp3_path):
                    os.remove(mp3_path)
            except Exception as cleanup_error:
                logger.warning(f"Cleanup error: {cleanup_error}")
    else:
        await update.message.reply_text("Sorry, I could not process the audio format.")

async def convert_audio(input_path: str) -> str:
    """Converts audio to MP3 using ffmpeg."""
    output_path = input_path.replace(".ogg", ".mp3")
    try:
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

async def process_agent_request(update: Update, content: Content, user_id: str, session_id: str):
    """Runs the agent and sends the response back to Telegram."""
    try:
        # Initialize Runner
        runner = Runner(
            agent=MANAGER_AGENT,
            app_name="telegram_assistant",
            session_service=session_service,
            auto_create_session=True
        )

        response_text = ""
        logger.info(f"Running agent for user {user_id}...")

        # Stream response
        async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        logger.info(f"Agent response: {response_text}")

        if response_text:
            await update.message.reply_text(response_text)
        else:
             await update.message.reply_text("I didn't have anything to say.")

    except Exception as e:
        logger.error(f"Error running agent: {e}")
        await update.message.reply_text("Sorry, I encountered an error processing your request.")

if __name__ == '__main__':
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables.")
        exit(1)

    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    text_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text)
    voice_handler = MessageHandler(filters.VOICE, handle_voice)

    application.add_handler(text_handler)
    application.add_handler(voice_handler)

    logger.info("Bot is running...")
    application.run_polling()
