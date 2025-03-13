import numpy as np
import faiss
import sqlite3
import re

from src.llm.llm import LLM


class SearchEngine:
    def __init__(self):
        """Initialise le pipeline"""
        self.llm = LLM()
        self.index_transcriptions = faiss.read_index("indexs/faiss_index_transcripts.bin")
        self.index_chapters = faiss.read_index("indexs/faiss_index_chapters.bin")
        self.db_path = 'src/videos_youtube.db'

    def search_similarity(self, prompt_embedding: list[float]):
        """Recherche l'embedding le plus proche du prompt"""
        #Recherche de similarité
        _, results = self.index_transcriptions.search(np.array([prompt_embedding]), k=1)
        
        #Formatage des résultats 
        if len(str(results[0][0])) == 5 :
            chunk_id = "00" + str(results[0][0]) 
            vid_id = str(results[0][0])[:1]
        elif len(str(results[0][0])) == 6:
            chunk_id = "0" + str(results[0][0]) 
            vid_id = str(results[0][0])[:2]
        else :
            chunk_id = str(results[0][0]) 
            vid_id = str(results[0][0])[:3]

        return {
            "prompt_embedding": prompt_embedding,
            "chunk_id": chunk_id,
            "vid_id": vid_id
        }

    def get_chunk_text(self, results_similarity: dict):
        """Récupère le texte du chunk le plus proche"""
        #Recupère l'url de la vidéo
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT chunks FROM chunks WHERE id = ?", (int(results_similarity["chunk_id"]),))
        result = cursor.fetchone()
        conn.close()

        chunk_text = result[0]

        return chunk_text


    def search_similar_chapter(self, results_similarity: dict):
        """Recherche le chapitre associé au chunk sélectionné"""
        #Recherche de similarité
        _, results = self.index_chapters.search(np.array([results_similarity["prompt_embedding"]], np.float32), k=1)

        #Formatage des résultats 
        if len(str(results[0][0])) == 4 :
            chapter_id = str(results[0][0])[-4:]
            vid_id = str(results[0][0])[:1]
        elif len(str(results[0][0])) == 5 :
            chapter_id = str(results[0][0])[-4:]
            vid_id = str(results[0][0])[:2]
        else :
            chapter_id = str(results[0][0])[-4:]
            vid_id = str(results[0][0])[:3]

        if results_similarity["vid_id"] == vid_id : 
            return {
                "chapter_id" : chapter_id,
                "vid_id" : vid_id
            }

        else :
            return {
                "chapter_id" : None,
                "vid_id" : vid_id
            }

    def search_vid_url(self, id_vid, chapter_id):
        """Retourne l'URL de la vidéo associée à un ID donné"""
        #Recupère l'url de la vidéo
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT url FROM videos WHERE id = ?", (id_vid,))
        result = cursor.fetchone()
        conn.close()

        video_url = result[0]

        #Récupère l'ID Youtube de la vidéo 
        match = re.search(r"(?<=v=)[\w-]+", video_url)
        id_yt_vid = match.group(0)

        if chapter_id is not None :
            #Récupère le timestamp du chapitre
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp FROM video_chapters WHERE id = ?", (chapter_id,))
            result = cursor.fetchone()
            conn.close()

            chapter_timestamp = result[0]

            #Converti le timestamp MM:SS en secondes
            minutes, seconds = map(int, chapter_timestamp.split(':'))
            total_seconds = minutes * 60 + seconds

            #Construction de l'URL avec le timestamp
            video_url_with_timestamp = f"https://www.youtube.com/embed/{id_yt_vid}?start={total_seconds}"

            return video_url_with_timestamp

        else : 
            return f"https://www.youtube.com/embed/{id_yt_vid}?start=0"

    def get_full_search_results(self, prompt: str):
        """Centralise et retourne tous les résultats sous forme de dictionnaire"""
        # Étape 1: Générer l'embedding du prompt
        prompt_embedding = self.llm.generate_prompt_embedding(prompt)

        # Étape 2: Recherche du chunk le plus similaire
        similarity_results = self.search_similarity(prompt_embedding)

        # Etape 3: Récupère le texte du chunk le plus similaire
        text_chunk = self.get_chunk_text(similarity_results)

        # Étape 4: Recherche du chapitre associé
        chapter_results = self.search_similar_chapter(similarity_results)

        # Étape 5: Récupérer l'URL de la vidéo avec le timestamp du chapitre
        video_url = self.search_vid_url(similarity_results["vid_id"], chapter_results["chapter_id"])

        # Retourner tous les résultats dans un seul dictionnaire
        full_results = {
            "chunk_id" : similarity_results["chunk_id"],
            "chunk_text" : text_chunk,
            "vid_id": similarity_results["vid_id"],
            "chapter_id": chapter_results["chapter_id"],
            "video_url_with_timestamp": video_url
        }

        return full_results