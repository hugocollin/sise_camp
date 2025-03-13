import sqlite3
import numpy as np
import faiss
from src.llm.llm import LLM
from src.preprocessing.preprocess import TextProcessor

processor = TextProcessor()

class Pipeline_Transcript_Faiss:
    def __init__(self):
        """Initialise la pipeline avec la base de données, l'index Faiss et le modèle LLM."""
        self.db_path = "../videos_youtube.db"
        self.index = faiss.read_index("../../indexs/faiss_index_transcripts.bin")
        self.llm = LLM()
        self.processor = processor

    def get_transcription(self, id_video: int) -> str:
        """Récupère la transcription d'une vidéo depuis la base de données."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT transcription FROM videos WHERE id={id_video}")
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]  # Retourne la transcription
        else:
            raise ValueError(f"No transcription found for video id {id_video}")

    def generate_chunk_ids(self, input_list: list[tuple[int, str | None]]) -> list[tuple[str, list[str]]]:
        """Génère une liste d'ID de chunks avec tokenisation et découpage."""
        chunk_list = []

        for original_id, text in input_list:
            if text is None:
                continue

            # Traitement du texte avec la classe TextProcessor
            chunks = self.processor.process_text(text)

            for chunk_id, chunk in enumerate(chunks, start=1):
                formatted_id = f"{original_id:02d}{chunk_id:04d}"
                chunk_list.append((formatted_id, chunk))

        return chunk_list

    def add_chunk_to_db(self, chunk_list: list[tuple[str, list[str]]]):
        """Ajoute les chunks à la base de données après avoir joint les tokens."""
        if len(str(chunk_list[0][0])) == 5:
            vid_id = str(chunk_list[0][0])[:1]
        else:
            vid_id = str(chunk_list[0][0])[:2]

        # Connexion à la base de données
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Préparer et insérer les chunks dans la table chunks
        for chunk in chunk_list:
            chunk_id, chunk_tokens = chunk
            chunk_data = " ".join(chunk_tokens)

            cursor.execute("INSERT INTO chunks (id, video_id, chunks) VALUES (?, ?, ?)", 
                           (chunk_id, vid_id, chunk_data))

        # Commit des changements et fermeture de la connexion
        conn.commit()
        conn.close()

    def add_embed_to_index(self, chunk_list: list[tuple[str, list[str]]]):
        """Ajoute les embeddings des chunks à l'index Faiss."""
        # Générer les embeddings
        embeddings_with_ids = self.llm.generate_chunks_embeddings(chunk_list)

        # Initialiser les deux listes pour les IDs et les embeddings
        ids = []
        embeddings = []

        # Séparer les IDs et les embeddings
        for chunk_id, embedding in embeddings_with_ids:
            ids.append(chunk_id)  # Ajouter l'ID
            embeddings.append(embedding)  # Ajouter l'embedding

        # Convertir les embeddings en tableau NumPy
        embeddings_np = np.array(embeddings).astype(np.float32)

        # Convertir les IDs en tableau NumPy
        ids_np = np.array(ids).astype(np.int64)

        # Ajouter les embeddings à l'index Faiss avec les IDs
        self.index.add_with_ids(embeddings_np, ids_np)

        print(f"Ajouté {len(embeddings_with_ids)} embeddings à l'index Faiss.")

    def run_pipeline(self, id_video: int):
        """Exécute tout le pipeline pour un id_video donné."""
        print(f"Démarrage du pipeline pour la vidéo ID {id_video}.")

        # 1. Récupérer la transcription
        transcription = self.get_transcription(id_video)
        print(f"Transcription récupérée pour la vidéo {id_video}.")

        # 2. Générer les chunks avec leurs IDs
        chunk_list = self.generate_chunk_ids([(id_video, transcription)])
        print(f"Chunks générés pour la vidéo {id_video}.")

        # 3. Ajouter les chunks à la base de données
        self.add_chunk_to_db(chunk_list)
        print(f"Chunks ajoutés à la base de données pour la vidéo {id_video}.")

        # 4. Ajouter les embeddings à l'index Faiss
        self.add_embed_to_index(chunk_list)
        print(f"Embeddings ajoutés à l'index Faiss pour la vidéo {id_video}.")

        print(f"Pipeline terminé pour la vidéo ID {id_video}.")