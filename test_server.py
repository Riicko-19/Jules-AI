from fastapi.testclient import TestClient
from server import app
from unittest.mock import patch, MagicMock, AsyncMock
import pytest

client = TestClient(app)

def test_verify_webhook():
    # Patch the global variable in server module
    with patch("server.WHATSAPP_TOKEN", "TEST_TOKEN"):
        response = client.get("/webhook?hub.verify_token=TEST_TOKEN&hub.challenge=CHALLENGE")
        assert response.status_code == 200
        assert response.text == "CHALLENGE"

@pytest.mark.asyncio
async def test_post_webhook_text():
    # Since TestClient calls the app directly, we can patch dependencies.
    # Note: TestClient runs sync.

    with patch("server.WHATSAPP_TOKEN", "TEST_TOKEN"), \
         patch("server.Runner") as MockRunner, \
         patch("server.send_whatsapp_message", new_callable=AsyncMock) as mock_send:

        # Mock Runner instance
        mock_runner_instance = MagicMock()
        MockRunner.return_value = mock_runner_instance

        # Mock run_async to yield an event with text
        async def mock_run_async(*args, **kwargs):
            event = MagicMock()
            part = MagicMock()
            part.text = "Hello response"
            event.content.parts = [part]
            yield event

        mock_runner_instance.run_async = mock_run_async

        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "1234567890",
                            "type": "text",
                            "text": {"body": "Hi"}
                        }]
                    }
                }]
            }]
        }

        response = client.post("/webhook", json=payload)
        assert response.status_code == 200

        # Verify Runner was initialized
        assert MockRunner.called

        # Verify send_whatsapp_message was called
        mock_send.assert_called_with("1234567890", "Hello response")

def test_post_webhook_audio():
     with patch("server.WHATSAPP_TOKEN", "TEST_TOKEN"), \
         patch("server.Runner") as MockRunner, \
         patch("server.send_whatsapp_message", new_callable=AsyncMock) as mock_send, \
         patch("server.download_audio", new_callable=AsyncMock) as mock_download, \
         patch("server.convert_audio", new_callable=AsyncMock) as mock_convert, \
         patch("builtins.open", new_callable=MagicMock) as mock_open, \
         patch("os.remove") as mock_remove:

        # Mocks
        mock_download.return_value = "test.ogg"
        mock_convert.return_value = "test.mp3"

        # Mock file read
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

        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "1234567890",
                            "type": "audio",
                            "audio": {"id": "media_id"}
                        }]
                    }
                }]
            }]
        }

        response = client.post("/webhook", json=payload)
        assert response.status_code == 200

        mock_download.assert_called_with("media_id")
        mock_convert.assert_called_with("test.ogg")
        mock_send.assert_called_with("1234567890", "Audio processed")
