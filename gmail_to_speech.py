import argparse
import os
import pickle
import time

import requests
from googleapiclient.discovery import build


def get_header(headers, key):
    for item in headers:
        if item.get("name", "").lower() == key.lower():
            return item.get("value", "")
    return ""


def fetch_emails(service, max_results, query):
    response = service.users().messages().list(
        userId="me",
        maxResults=max_results,
        q=query if query else None,
    ).execute()
    return response.get("messages", [])


def build_email_text(index, msg_data):
    headers = msg_data.get("payload", {}).get("headers", [])
    sender = get_header(headers, "From") or "Unknown sender"
    subject = get_header(headers, "Subject") or "No subject"
    snippet = (msg_data.get("snippet") or "").strip()

    if snippet:
        return (
            f"Email {index}. From {sender}. Subject: {subject}. "
            f"Preview: {snippet}"
        )
    return f"Email {index}. From {sender}. Subject: {subject}."


def text_to_speech(api_key, voice_id, text, output_path):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5,
        },
    }

    response = requests.post(url, json=payload, headers=headers, timeout=60)
    if response.status_code != 200:
        raise RuntimeError(
            f"ElevenLabs error ({response.status_code}): {response.text}"
        )

    with open(output_path, "wb") as out_file:
        out_file.write(response.content)


def main():
    parser = argparse.ArgumentParser(
        description="Read different Gmail emails and save speech audio files."
    )
    parser.add_argument(
        "--count",
        type=int,
        default=3,
        help="How many latest emails to read (default: 3).",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="",
        help='Optional Gmail search query, e.g. "is:unread" or "from:amazon".',
    )
    parser.add_argument(
        "--voice-id",
        type=str,
        default="pNInz6obpgDQGcFmaJgB",
        help="ElevenLabs voice ID.",
    )
    args = parser.parse_args()

    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError(
            "Missing ELEVENLABS_API_KEY environment variable. "
            "Set it before running this script."
        )

    with open("token.pickle", "rb") as token_file:
        creds = pickle.load(token_file)

    service = build("gmail", "v1", credentials=creds)
    messages = fetch_emails(service, args.count, args.query)

    if not messages:
        print("No emails found for the given query.")
        return

    for idx, msg in enumerate(messages, start=1):
        msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        email_text = build_email_text(idx, msg_data)
        file_name = f"email_{idx}.mp3"

        print(f"\nProcessing email {idx}:")
        print(email_text)

        text_to_speech(api_key, args.voice_id, email_text, file_name)
        print(f"Saved: {file_name}")
        print("-" * 40)
        time.sleep(1.5)


if __name__ == "__main__":
    main()