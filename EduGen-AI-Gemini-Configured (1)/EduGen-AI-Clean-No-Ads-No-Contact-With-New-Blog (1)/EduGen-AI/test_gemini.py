
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env", override=True)

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("LLM_API_KEY")

if not api_key:
    print("ERROR: API key not found")
    raise SystemExit(1)

url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"

payload = {
    "contents": [{
        "parts": [{
            "text": "Explain Artificial Intelligence in 5 simple lines."
        }]
    }]
}

try:
    response = requests.post(
        url,
        params={"key": api_key},
        json=payload,
        timeout=90
    )

    print("\nHTTP STATUS:", response.status_code)

    data = response.json()

    if response.ok:
        answer = data["candidates"][0]["content"]["parts"][0]["text"]
        print("\nGEMINI ANSWER:\n")
        print(answer)
    else:
        print("\nGEMINI API ERROR:")
        print(data)

except requests.exceptions.RequestException as e:
    print("CONNECTION ERROR:", e)
except (KeyError, IndexError, TypeError) as e:
    print("RESPONSE PARSING ERROR:", e)
    print(data)

