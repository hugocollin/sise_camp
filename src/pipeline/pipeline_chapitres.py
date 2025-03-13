import sqlite3
import numpy as np
import faiss
import time
from src.llm.llm import LLM

class Pipeline_Chapters_Faiss:
    def __init__(self):
        """Initialise la pipeline avec la base de données, l'index Faiss et le modèle LLM."""
        self.db_path = "src/videos_youtube.db"
        self.index = faiss.read_index("indexs/faiss_index_chapters.bin")
        self.llm = LLM()

    def get_chapters(self, id_video: int) -> str:
        """Récupère les chapitres d'une vidéo depuis la base de données."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, video_id, subtitle FROM video_chapters WHERE video_id = {id_video}")
        results = cursor.fetchall()
        conn.close()

        if results == []:
            return None
        else:
            return results

    def get_chapters_embeddings_ids(self, results):
        """Génère les embeddings des chapitres"""
        # Extraire uniquement les titres (le troisième élément de chaque tuple)
        chapters = [chap for _, _, chap in results]

        #Initialisation d'une liste pour les embeddings des chapitres 
        list_embd = []

        #Génère les embeddings
        for chap in chapters:
            list_embd.append(self.llm.generate_prompt_embedding(chap))
            time.sleep(2)

        #Générer la liste des nouveaux IDs
        new_ids = [f"{grp:02}{id_:03}" for id_, grp, _ in results]

        return [list_embd, new_ids]


    def add_embed_to_index(self, embd_ids_list: list[list[str], list[float]]):
        """Ajoute les embeddings des chapitres à l'index Faiss."""
        # Convertir les embeddings en tableau NumPy
        embeddings = np.array(embd_ids_list[0]).astype(np.float32)

        # Convertir les IDs en tableau NumPy
        ids = np.array(embd_ids_list[1]).astype(np.int64)

        # Ajouter les embeddings à l'index Faiss avec les IDs
        self.index.add_with_ids(embeddings, ids)

        # Sauvegarde des modifications
        faiss.write_index(self.index, "indexs/faiss_index_chapters.bin")

        print(f"Ajouté {len(embd_ids_list)} embeddings à l'index Faiss.")

    def run_pipeline(self, id_video: int):
        """Exécute tout le pipeline pour un id_video donné."""
        print(f"Démarrage du pipeline 'Chapitres' pour la vidéo ID {id_video}.")

        # 1. Récupérer les chapitres
        chapitres = self.get_chapters(id_video)
        print(f"Chapitres récupérés pour la vidéo {id_video}.")

        if chapitres is not None : 
            # 2. Générer les embeddings avec leurs IDs
            embed_list = self.get_chapters_embeddings_ids(chapitres)
            print(f"Embeddings des chapitres générés pour la vidéo {id_video}.")

            # 3. Ajouter les embeddings à l'index Faiss
            self.add_embed_to_index(embed_list)
            print(f"Embeddings des chapitres ajoutés à l'index Faiss pour la vidéo {id_video}.")

            print(f"Pipeline Chapitres terminé pour la vidéo ID {id_video}.")