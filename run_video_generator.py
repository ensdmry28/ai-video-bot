
import os
from openai import OpenAI
from moviepy.editor import *
import requests
from elevenlabs import generate, save, set_api_key
import json
import time
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

# Ayarlar
openai_api_key = os.getenv("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")
eleven_api_key = os.getenv("sk_9f5f145814f5e0d82d5b9e738f3219ed41eb6eb5399d06ba")
client_secret_file = "client_secret.json"

set_api_key(eleven_api_key)
client = OpenAI(api_key=openai_api_key)

# 1. Konu oluştur
def generate_topic():
    prompt = "Bugün için ilginç bir bilimsel gerçek öner."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0
    )
    return response.choices[0].message.content.strip()

# 2. Senaryo üret
def generate_script(topic):
    prompt = f"{topic} konusuyla ilgili, eğlenceli ve bilgilendirici bir video senaryosu yaz. Maksimum 80 kelime olsun."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0
    )
    return response.choices[0].message.content.strip()

# 3. Görsel oluştur
def generate_image(prompt, filename="image.png"):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1
    )
    image_url = response.data[0].url
    img_data = requests.get(image_url).content
    with open(filename, 'wb') as handler:
        handler.write(img_data)
    return filename

# 4. Ses üret
def generate_voice(text, filename="voice.mp3"):
    audio = generate(text=text, voice="7VqWGAWwo2HMrylfKrcm", model="eleven_multilingual_v2")
    save(audio, filename)
    return filename

# 5. Video oluştur
def generate_video(image_path, audio_path, output_path="final_video.mp4"):
    audioclip = AudioFileClip(audio_path)
    imageclip = ImageClip(image_path).set_duration(audioclip.duration).set_audio(audioclip).resize(height=1080)
    imageclip.write_videofile(output_path, fps=24)
    return output_path

# 6. YouTube’a yükle
def upload_to_youtube(video_path, title, description):
    scopes = ["https://www.googleapis.com/auth/youtube.upload"]
    credentials = service_account.Credentials.from_service_account_file(client_secret_file, scopes=scopes)
    youtube = build("youtube", "v3", credentials=credentials)

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": ["bilim", "gerçekler", "yapay zeka"],
            "categoryId": "27"
        },
        "status": {
            "privacyStatus": "public"
        }
    }

    mediaFile = MediaFileUpload(video_path)
    youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=mediaFile
    ).execute()

# 🔁 Ana Akış
if __name__ == "__main__":
    topic = generate_topic()
    print("Konu:", topic)

    script = generate_script(topic)
    print("Senaryo:", script)

    image_path = generate_image(script)
    audio_path = generate_voice(script)
    video_path = generate_video(image_path, audio_path)

    upload_to_youtube(video_path, title=topic, description=script)
