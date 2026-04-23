import requests

API_KEY = "sk_7ade3bb919703219ab6cf7128eb43e974715b166c471efc5"

url =  "https://api.elevenlabs.io/v1/text-to-speech/EXAVITQu4vr4xnSDxMaL"

headers = {
    "xi-api-key": API_KEY,
    "Content-Type": "application/json"
}

data = {
    "text": "Hello Aman, this is your ElevenLabs project working successfully!",
    "voice_settings": {
        "stability": 0.75,
        "similarity_boost": 0.85,
        "style":0.6,
        "use_speaker_boost":True
    }
}

response = requests.post(url, json=data, headers=headers)

with open("output.mp3", "wb") as f:
    f.write(response.content)

print("Audio file saved as output.mp3")