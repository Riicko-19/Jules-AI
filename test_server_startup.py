import time
import requests
import subprocess
import signal
import os

def test_server():
    print("Starting server...")
    env = os.environ.copy()
    env["WHATSAPP_TOKEN"] = "TEST_TOKEN"

    process = subprocess.Popen(["uvicorn", "server:app", "--port", "8000"], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5) # Wait for startup

    try:
        print("Testing verify webhook...")
        response = requests.get("http://localhost:8000/webhook?hub.verify_token=TEST_TOKEN&hub.challenge=CHALLENGE")
        print(f"Verify Response: {response.status_code}, {response.text}")
        assert response.status_code == 200
        assert response.text == "CHALLENGE"

        # Test post webhook (mock)
        print("Testing post webhook...")
        payload = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": "1234567890",
                            "type": "text",
                            "text": {"body": "Hello"}
                        }]
                    }
                }]
            }]
        }
        # Note: This will trigger agent run which will fail due to missing GEMINI_API_KEY, but endpoint handles exception and logs it.
        response = requests.post("http://localhost:8000/webhook", json=payload)
        print(f"Post Response: {response.status_code}, {response.json()}")
        assert response.status_code == 200

    except Exception as e:
        print(f"Test failed: {e}")

    finally:
        print("Stopping server...")
        os.kill(process.pid, signal.SIGTERM)
        stdout, stderr = process.communicate()
        print(f"Server Output: {stdout.decode()}")
        print(f"Server Error: {stderr.decode()}")

if __name__ == "__main__":
    test_server()
