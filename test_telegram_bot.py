import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from server import handle_text, handle_voice
from google.genai.types import Content

@pytest.mark.asyncio
async def test_handle_text():
    # Mock Update and Context
    update = MagicMock()
    update.effective_user.id = 12345
    update.message.text = "Hello"
    update.message.reply_text = AsyncMock()

    context = MagicMock()

    # Mock Runner
    with patch("server.Runner") as MockRunner:
        mock_runner_instance = MagicMock()
        MockRunner.return_value = mock_runner_instance

        async def mock_run_async(*args, **kwargs):
            event = MagicMock()
            part = MagicMock()
            part.text = "Hello response"
            event.content.parts = [part]
            yield event

        mock_runner_instance.run_async = mock_run_async

        await handle_text(update, context)

        # Verify Runner initialization
        assert MockRunner.called
        # Verify reply
        update.message.reply_text.assert_called_with("Hello response")

@pytest.mark.asyncio
async def test_handle_voice():
    # Mock Update and Context
    update = MagicMock()
    update.effective_user.id = 12345
    update.message.voice.file_id = "file_id"
    update.message.reply_text = AsyncMock()

    context = MagicMock()
    voice_file = MagicMock()
    voice_file.download_to_drive = AsyncMock()
    context.bot.get_file = AsyncMock(return_value=voice_file)

    # Mock file operations and Runner
    with patch("server.Runner") as MockRunner, \
         patch("server.convert_audio", new_callable=AsyncMock) as mock_convert, \
         patch("builtins.open", new_callable=MagicMock) as mock_open, \
         patch("os.remove") as mock_remove:

        mock_convert.return_value = "test.mp3"

        mock_file = MagicMock()
        mock_file.__enter__.return_value = mock_file
        mock_file.read.return_value = b"audio data"
        mock_open.return_value = mock_file

        mock_runner_instance = MagicMock()
        MockRunner.return_value = mock_runner_instance

        async def mock_run_async(*args, **kwargs):
            event = MagicMock()
            part = MagicMock()
            part.text = "Audio processed"
            event.content.parts = [part]
            yield event

        mock_runner_instance.run_async = mock_run_async

        await handle_voice(update, context)

        # Verify
        context.bot.get_file.assert_called_with("file_id")
        voice_file.download_to_drive.assert_called()
        mock_convert.assert_called()
        update.message.reply_text.assert_called_with("Audio processed")
