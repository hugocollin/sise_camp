"""
Ce fichier contient le pipeline de traitement des données des informations d'une vidéo YouTube.
"""

import os
from io import BytesIO
import requests
import yt_dlp
import streamlit as st
from pydub import AudioSegment

from src.llm.llm import LLM
from src.db.db_youtube import YouTubeManager


class Pipeline:
    """
    Classe pour l'ajout d'une vidéo YouTube.
    """

    def __init__(self, url):
        """
        Initialise la classe avec l’URL de la vidéo YouTube.

        Args:
            url (str): URL de la vidéo YouTube.
        """
        self.url = url
        self.llm = LLM()
        self.db_manager = YouTubeManager()

    def get_mp3(self) -> str:
        """
        Récupère le fichier audio de la vidéo YouTube au format MP3.

        Returns:
            str: Nom du fichier MP3.
        """
        options = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
            "outtmpl": "%(title)s.mp3",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36",
        }
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([self.url])
        mp3_files = [f for f in os.listdir() if f.endswith(".mp3")]
        return mp3_files[0]

    def audio_chunks(self, mp3_file: str, chunk_length_ms: int = 600000):
        """
        Découpe un fichier audio en segments de 10 minutes maximum.

        Args:
            mp3_file (str): Nom du fichier audio à découper.
            chunk_length_ms (int, optional): Longueur des segments en millisecondes. Defaults to 600000.

        Returns:
            list: Liste des segments audio.
        """
        audio = AudioSegment.from_file(mp3_file, format="mp3")
        if len(audio) > chunk_length_ms:
            chunks = []
            for i in range(0, len(audio), chunk_length_ms):
                chunks.append(audio[i : i + chunk_length_ms])
            return chunks
        else:
            return [audio]

    def get_transcription(self, chunk_audio: AudioSegment) -> str:
        """
        Envoie un fichier audio à l'API Whisper et récupère la transcription.

        Args:
            chunk_audio (AudioSegment): Segment audio à transcrire.

        Returns:
            str: Transcription du segment audio.
        """
        buf = BytesIO()
        chunk_audio.export(buf, format="mp3")
        buf.seek(0)
        response = requests.post(
            "https://api-inference.huggingface.co/models/openai/whisper-large-v3-turbo",
            headers={
                "Authorization": f"Bearer {st.session_state['huggingface_api_key']}"
            },
            data=buf.read(),
            timeout=300,
        )
        try:
            result = response.json()
            return result.get("text", response.text)
        except Exception:
            return response.text

    def transcribe_audio(self, chunks) -> str:
        """
        Transcrit l’ensemble des segments audio et renvoie la transcription complète.

        Args:
            chunks (list): Liste des segments audio.

        Returns:
            str: Transcription complète.
        """
        if len(chunks) > 1:
            transcription_parts = []
            for chunk in chunks:
                text_part = self.get_transcription(chunk)
                transcription_parts.append(text_part)
            return " ".join(transcription_parts)
        else:
            return self.get_transcription(chunks[0])

    def transcription_enhancement(self, transcription: str) -> str:
        """
        Améliore la transcription en utilisant un modèle de langage.

        Args:
            transcription (str): Transcription à améliorer.

        Returns:
            str: Transcription améliorée.
        """

        transcription = self.llm.call_model(
            provider="mistral",
            model="mistral-large-latest",
            temperature=0.5,
            prompt_dict=[
                {
                    "role": "user",
                    "content": f"À partir de la transcription de l'audio d'une vidéo YouTube, corrige et améliore ce texte pour obtenir un français clair, fluide et sans fautes. Assure-toi d’éliminer les répétitions ou erreurs éventuelles, et préserve le sens général de la vidéo : {transcription}",
                }
            ],
        )
        return transcription

    def create_summary(self, transcription: str) -> str:
        """
        Crée un résumé de la transcription.

        Args:
            transcription (str): Transcription de la vidéo.

        Returns:
            str: Résumé de la transcription.
        """
        summary = self.llm.call_model(
            provider="mistral",
            model="mistral-large-latest",
            temperature=0.7,
            prompt_dict=[
                {
                    "role": "user",
                    "content": f"Crée un résumé de la transcription de l'audio d'une vidéo YouTube. Le résumé doit être concis et refléter les idées principales de la vidéo : {transcription}",
                }
            ],
        )
        return summary

    def update_video_info(self, transcription: str, summary: str) -> bool:
        """
        Met à jour la base de données avec la transcription et le résumé de la vidéo.
        """
        self.db_manager.add_transcription(self.url, transcription)
        self.db_manager.add_resume(self.url, summary)
