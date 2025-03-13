import yt_dlp
import sqlite3
import re
import time
import os.path

class YouTubeManager:
    """
    Classe pour gérer les vidéos YouTube, extraire leurs informations
    et les stocker dans une base de données SQLite.
    """

    def __init__(self, db_path='src/videos_youtube.db'):
        """
        Initialise le gestionnaire de vidéos YouTube.
        
        Args:
            db_path (str): Chemin vers la base de données SQLite
        """
        self.db_path = db_path
        self._setup_database()

    def _setup_database(self):
        """
        Configure la structure de la base de données et ajoute la colonne `parsed` si elle n'existe pas.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Création de la table `videos` si elle n'existe pas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            title TEXT,
            upload_date TEXT,
            description TEXT,
            duration INTEGER, 
            transcription TEXT, 
            resume TEXT
        )
        ''')

        # Vérifier si la colonne `parsed` existe, sinon l'ajouter
        cursor.execute("PRAGMA table_info(videos)")
        columns = [col[1] for col in cursor.fetchall()]
        if "parsed" not in columns:
            cursor.execute("ALTER TABLE videos ADD COLUMN parsed BOOLEAN DEFAULT TRUE")
            conn.commit()

        # Création de la table `tags`
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            tag_name TEXT,
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
        ''')

        # Création de la table `video_chapters`
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS video_chapters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER,
            timestamp TEXT,
            subtitle TEXT,
            FOREIGN KEY (video_id) REFERENCES videos (id)
        )
        ''')

        conn.commit()
        conn.close()
    
    def extract_chapters(self, description):
        """
        Extrait les timestamps et sous-titres de la description d'une vidéo.
        
        Args:
            description (str): Description de la vidéo
            
        Returns:
            list: Liste de tuples (timestamp, sous-titre)
        """
        pattern = r'(\d{2}:\d{2}) (.+)'
        matches = re.findall(pattern, description)
        return matches
    
    def clean_description(self, description):
        """
        Supprime les lignes de timestamps de la description.
        
        Args:
            description (str): Description originale
            
        Returns:
            str: Description nettoyée
        """
        lines = description.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # If the line doesn't match the timestamp pattern, keep it
            if not re.match(r'^\d{2}:\d{2} .+', line.strip()):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def get_video_info(self, url):
        """
        Récupère les informations d'une vidéo YouTube.
        
        Args:
            url (str): URL de la vidéo YouTube
            
        Returns:
            dict: Informations de la vidéo
        """
        ydl_opts = {
            'quiet': True,        
            'no_warnings': True,  
            'skip_download': True 
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

            original_description = info.get('description', 'No description available')
            
            # Extract chapters first
            chapters = self.extract_chapters(original_description)
            
            # Then remove timestamp lines from description
            cleaned_description = self.clean_description(original_description)

            video_data = {
                'url': url,
                'title': info.get('title', 'Unknown'),
                'upload_date': info.get('upload_date', 'Unknown'),
                'description': cleaned_description,
                'duration': info.get('duration', 0),
                'tags': info.get('tags', []),
                'chapters': chapters, 
                'transcription': None, 
                'resume': None
            }

            return video_data
        except Exception as e:
            print(f" Error getting info for {url}: {str(e)}")
            return None

    def url_exists(self, url):
        """
        Vérifie si une URL existe déjà dans la base de données.
        
        Args:
            url (str): URL à vérifier
            
        Returns:
            bool: True si l'URL existe déjà, False sinon
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT id FROM videos WHERE url = ?', (url,))
            result = cursor.fetchone()
            return result is not None
        except sqlite3.OperationalError:

            return False
        finally:
            conn.close()
    

    def save_video(self, video_info, parsed):
        """
        Enregistre les informations d'une vidéo dans la base de données.
        
        Args:
            video_info (dict): Informations de la vidéo à enregistrer
            parsed (bool): Indique si la vidéo a déjà été analysée ou non
        """
        if video_info is None:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insérer ou mettre à jour la vidéo avec `parsed`
        cursor.execute('''
        INSERT OR REPLACE INTO videos (url, title, upload_date, description, duration, transcription, resume, parsed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            video_info['url'],
            video_info['title'],
            video_info['upload_date'],
            video_info['description'],
            video_info['duration'], 
            video_info['transcription'], 
            video_info['resume'],
            parsed  # ✅ Ajouter la valeur `parsed`
        ))

        video_id = cursor.lastrowid 

        # Insérer les tags
        if 'tags' in video_info and video_info['tags']:
            for tag in video_info['tags']:
                cursor.execute('''
                INSERT INTO tags (video_id, tag_name)
                VALUES (?, ?)
                ''', (video_id, tag))

        # Insérer les chapitres
        if 'chapters' in video_info and video_info['chapters']:
            for timestamp, subtitle in video_info['chapters']:
                cursor.execute('''
                INSERT INTO video_chapters (video_id, timestamp, subtitle)
                VALUES (?, ?, ?)
                ''', (video_id, timestamp, subtitle))

        conn.commit()
        conn.close()

    def process_video(self, url):
        """
        Traite une vidéo YouTube : vérifie si elle existe déjà,
        récupère ses informations et les enregistre.
        
        Args:
            url (str): URL de la vidéo
            
        Returns:
            dict or None: Informations de la vidéo si elle a été traitée, None sinon
        """
        if self.url_exists(url):
            print(f" Video already exists: {url}")
            return None
        
        try:
            video_info = self.get_video_info(url)
            if video_info:
                self.save_video(video_info, parsed=False)  # ✅ Ajouter les nouvelles vidéos avec `parsed=False`
                return video_info
            return None
        except Exception as e:
            print(f" Error processing video {url}: {e}")
            return None

    def add_transcription(self, url, transcription_text):
        """
        Ajoute une transcription fournie à une vidéo existante dans la base de données.
        
        Args:
            url (str): URL de la vidéo
            transcription_text (str): Texte de transcription à ajouter
                
        Returns:
            bool: True si la transcription a été ajoutée avec succès, False sinon
        """
        print(f"\nAdding transcription for URL: {url}")
        
        if not self.url_exists(url):
            print(f"Video does not exist in database: {url}")
            return False
        
        try:
            # Mettre à jour la base de données avec la transcription
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE videos 
            SET transcription = ? 
            WHERE url = ?
            ''', (transcription_text, url))
            
            conn.commit()
            conn.close()
            
            print(f"Successfully added transcription for video: {url}")
            return True
        except Exception as e:
            print(f"Error adding transcription for URL {url}: {str(e)}")
            return False

    def add_resume(self, url, resume):
        """
        Ajoute une transcription fournie à une vidéo existante dans la base de données.
        
        Args:
            url (str): URL de la vidéo
            resume (str): Resumé à ajouter
                
        Returns:
            bool: True si le résumé a été ajouté avec succès, False sinon
        """
        print(f"\nAdding Résumé for URL: {url}")
        
        if not self.url_exists(url):
            print(f"Video does not exist in database: {url}")
            return False
        
        try:
            # Mettre à jour la base de données avec la transcription
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
            UPDATE videos 
            SET resume = ? 
            WHERE url = ?
            ''', (resume, url))
            
            conn.commit()
            conn.close()
            
            print(f"Successfully added transcription for video: {url}")
            return True
        except Exception as e:
            print(f"Error adding transcription for URL {url}: {str(e)}")
            return False

    def process_videos_from_file(self, file_path):
        """
        Traite les URLs de vidéos YouTube contenues dans un fichier pour les ajouter à la base de données.
        
        Args:
            file_path (str): Chemin vers le fichier contenant les URLs
        """
        if not os.path.isfile(file_path):
            print(f" File not found: {file_path}")
            return
            
        processed = 0
        errors = 0
        skipped = 0
            
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                url = line.strip()
                if not url or url.startswith("#"):
                    continue
                    
                print(f"\n Processing URL {line_num}: {url}")
                
                if self.url_exists(url):
                    print(f" Video already exists: {url}")
                    skipped += 1
                    continue
                
                try:
                    video_info = self.process_video(url)
                    if video_info:
                        processed += 1
                    else:
                        errors += 1
                    
                    time.sleep(1.5)
                except Exception as e:
                    print(f" Error processing URL {url}: {str(e)}")
                    errors += 1
        
        print(f"\n Processed: {processed}, Skipped: {skipped}, Errors: {errors}")
    
    def reset_database(self):
        """
        Réinitialise la base de données en supprimant toutes les données.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM videos')
        cursor.execute('DELETE FROM tags')
        cursor.execute('DELETE FROM video_chapters')
        
        conn.commit()
        conn.close()
        print(" Database reset successfully")
    
    def add_new_video(self, url):
        """
        Ajoute une URL YouTube à la base de données.
        
        Args:
            url (str): URL de la vidéo
            
        Returns:
            bool: True si la vidéo a été ajoutée avec succès, False sinon
        """
        print(f"\nProcessing URL: {url}")
        
        if self.url_exists(url):
            print(f"Video already exists: {url}")
            return False
        
        try:
            video_info = self.process_video(url)
            if video_info:
                print(f"Successfully added video: {video_info['title']}")
                return True
            return False
        except Exception as e:
            print(f"Error processing URL {url}: {str(e)}")
            return False
  
    def get_channel_videos(self, channel_url):
        """
        Récupère toutes les vidéos d'une chaîne YouTube.

        Args:
            channel_url (str): URL de la chaîne YouTube.

        Returns:
            list: Liste des URLs des vidéos.
        """
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,  # Ne pas télécharger, juste récupérer les URLs
            'skip_download': True
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                videos = [entry['url'] for entry in info.get('entries', [])]
                return videos
        except Exception as e:
            print(f"Erreur lors du scraping de la chaîne : {e}")
            return []

    def add_channel_videos(self, channel_url):
        """
        Ajoute toutes les vidéos d'une chaîne YouTube dans la base de données si elles ne sont pas déjà présentes.

        Args:
            channel_url (str): URL de la chaîne YouTube.
        """
        print(f"\nScraping videos from channel: {channel_url}")

        video_urls = self.get_channel_videos(channel_url)
        if not video_urls:
            print("Aucune vidéo trouvée sur la chaîne.")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Vérifier si la colonne 'parsed' existe dans la table videos
        cursor.execute("PRAGMA table_info(videos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "parsed" not in columns:
            cursor.execute("ALTER TABLE videos ADD COLUMN parsed BOOLEAN DEFAULT TRUE")
            conn.commit()

        for url in video_urls:
            if self.url_exists(url):
                print(f"Vidéo déjà en base : {url}")
                continue

            # Récupérer le titre de la vidéo
            try:
                with yt_dlp.YoutubeDL({'quiet': True, 'skip_download': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', 'Unknown')
            except Exception as e:
                print(f"Erreur en récupérant le titre pour {url} : {e}")
                title = "Unknown"

            # Ajouter la vidéo avec parsed = FALSE
            cursor.execute('''
            INSERT INTO videos (url, title, parsed) 
            VALUES (?, ?, ?)
            ''', (url, title, False))

            print(f"Ajouté à la base : {title}")

        conn.commit()
        conn.close()
        print("\nBase de données mise à jour avec les nouvelles vidéos de la chaîne.")


if __name__ == "__main__":
    db = YouTubeManager()
    
    # Pour initialiser la base de données avec les données dedans
    #db.process_videos_from_file("src/links.txt")

    # Pour insérer un résumé
    #db.add_resume("https://www.youtube.com/watch?v=gQYp_CYCGVM", "Ceci est un résumé tout à fait intéressant")

    # Pour ajouter une seule vidéo
    # db.add_new_video("https://www.youtube.com/watch?v=3KQG24jBpHg")

    # Pour ajouter une transcription à une vidéo existante
    # db.add_transcription("https://www.youtube.com/watch?v=gQYp_CYCGVM", "Ceci est une transcription de test ")

    channel_url = "https://www.youtube.com/@master2sisedatascience/videos"
    # ajouter le nom et le l'url des vidéos non scrapées à la base de données  
    db.add_channel_videos(channel_url)