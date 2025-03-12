import os
import requests
import yt_dlp
import streamlit as st

from src.llm.llm import LLM

class Transcriptor:
    def __init__(self, url):
        self.url = url

    def get_transcription(self):
        options = {
            'format': 'bestaudio/best',
            'extract_audio': True,
            'audio_format': 'mp3',
            'outtmpl': f'%(title)s.mp3',
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([self.url])
        
        mp3_files = [f for f in os.listdir() if f.endswith('.mp3')]
        mp3_file = mp3_files[0]
        with open(mp3_file, 'rb') as file:
            audio_data = file.read()

        response = requests.post(
            "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo",
            headers={"Authorization": f"Bearer {st.session_state["huggingface_api_key"]}"},
            data=audio_data,
            timeout=300
        )
        # [TEMP]
        print("Status Code :", response.status_code)
        print("Response Text :", response.text)

        result = response.json()
        transcription = result.get("text", response.text)

        llm = LLM()
        ai_transcription = llm.call_model(
            provider="mistral",
            model="ministral-8b-latest",
            temperature=0.5,
            prompt_dict=[{"role": "user", "content": f"À partir de la transcription de l'audio d'une vidéo YouTube, corrige et améliore ce texte pour obtenir un français clair, fluide et sans fautes. Assure-toi d’éliminer les répétitions ou erreurs éventuelles, et préserve le sens général du discours : {transcription}"}]
        )

        if os.path.exists(mp3_file):
            os.remove(mp3_file)

        return ai_transcription
