from googleapiclient.discovery import build
import pickle

# Load token
with open("token.pickle", "rb") as token:
    creds = pickle.load(token)

# Build service
service = build("gmail", "v1", credentials=creds)

# Get messages
results = service.users().messages().list(userId="me", maxResults=5).execute()
messages = results.get("messages", [])

print("Latest Emails:\n")

for msg in messages:
    msg_data = service.users().messages().get(userId="me", id=msg["id"]).execute()
    headers = msg_data["payload"]["headers"]

    subject = ""
    sender = ""

    for h in headers:
        if h["name"] == "Subject":
            subject = h["value"]
        if h["name"] == "From":
            sender = h["value"]

    print(f"From: {sender}")
    print(f"Subject: {subject}")
    print("-" * 40)