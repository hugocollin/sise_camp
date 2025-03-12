import os
import requests
import yt_dlp
import streamlit as st
from io import BytesIO
from pydub import AudioSegment

from src.llm.llm import LLM

class Transcriptor:
    """
    Classe pour transcrire une vidéo YouTube en texte.
    """
    def __init__(self, url):
        """
        Initialise la classe avec l’URL de la vidéo YouTube.

        Args:
            url (str): URL de la vidéo YouTube.
        """
        self.url = url

    def get_transcription(self):
        options = {
            'format': 'bestaudio/best',
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192'
                }
            ],
            'outtmpl': f'%(title)s.mp3',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([self.url])
        
        mp3_files = [f for f in os.listdir() if f.endswith('.mp3')]
        mp3_file = mp3_files[0]

        audio = AudioSegment.from_file(mp3_file, format="mp3")
        chunk_length_ms = 10 * 60000  # 10 minutes

        def send_chunk(chunk_audio):
            """Envoie un segment audio à l’API Whisper et renvoie le texte transcrit."""
            buf = BytesIO()
            chunk_audio.export(buf, format="mp3")
            buf.seek(0)
            response = requests.post(
                "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo",
                headers={"Authorization": f"Bearer {st.session_state['huggingface_api_key']}"},
                data=buf.read(),
                timeout=300
            )
            result = response.json()
            return result.get("text", response.text)

        # Si l’audio dépasse 10 minutes, on le découpe
        if len(audio) > chunk_length_ms:
            print("L'audio dépasse 10 minutes, découpage en segments...")
            transcription_parts = []
            for i in range(0, len(audio), chunk_length_ms):
                segment = audio[i:i+chunk_length_ms]
                text_part = send_chunk(segment)
                transcription_parts.append(text_part)
            transcription = " ".join(transcription_parts)
        else:
            # Sinon, on envoie directement l’audio complet
            with open(mp3_file, 'rb') as file:
                audio_data = file.read()
            response = requests.post(
                "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo",
                headers={"Authorization": f"Bearer {st.session_state['huggingface_api_key']}"},
                data=audio_data,
                timeout=300
            )
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
