# SISE Camp ⭐

Cette application Streamlit permet d'effectuer des recherches sur la transcription des vidéos youtube de la chaîne YouTube [MASTER 2 SISE DATA SCIENCE](https://www.youtube.com/@master2sisedatascience). 

## Plan

2. [Fonctionnalités](#fonctionnalités)
3. [Technologies Utilisées](#-technologies-utilisées)
4. [Structure du Projet](#-structure-du-projet)
5. [Installation](#-installation)
6. [Utilisation](#-utilisation)
7. [Contributions](#-contributions)
7. [Auteurs](#-auteurs)


## 🎯 Fonctionnalités

Ce projet permet aux utilisateurs de :

1. Effectuer des recherches dans la base de données. 
   
2. Obtenir la vidéo la plus pertinente en fonction de la recherche, accompagnée d'un résumé et du passage exact correspondant à la requête.
   
3. Ajouter de nouvelle vidéo provenant de la chaîne YoutTube [MASTER 2 SISE DATA SCIENCE](https://www.youtube.com/@master2sisedatascience) à la base de données. 
   
4.  Utiliser l'application en ligne ou l'exécuter localement.

## 🔧 Technologies Utilisées

- **Frontend** : Streamlit
- **Traitement Audio** : yt-dlp, pydub
- **Transcription** : Modèle Whisper de Hugging Face
- **Amélioration de Texte** : Mistral AI via LiteLLM
- **Moteur de Recherche** : FAISS
- **Base de Données** : SQLite

## 🗂️ Structure du Projet

## 🚀 Installation

Pour installer ce projet, clonez le dépôt sur votre machine locale, en utilisant la commande suivante :

```bash
git clone https://github.com/hugocollin/sise_camp.git
```

## 💻 Utilisation

Pour utiliser cette application vous avez 3 méthodes :
Attention pour les deux premières méthodes vous avez besoin de configurez un fichier .env à la racine du projet : 

```bash
MISTRAL_API_KEY=your_mistral_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
```
⚠️ Il ne doit pas y avoir d'espaces ou de guillemets pour les clés d'environnement.

### I. Utilisez l'application en local

1. Installez et activez un environnement Python avec une version 3.11.

2. Déplacez-vous à la racine du projet.

3. Exécutez la commande suivante pour installer les dépendances du projet :

```bash
pip install -r docker-requirements.txt
```

4. Exécutez la commande suivante pour lancer l'application :

```bash
streamlit run main.py
```

5. Ouvrez votre navigateur et accédez à l'adresse suivante : [http://localhost:8501](http://localhost:8501)

### II. Utilisez l'application avec Docker

1. Installez et demarrez [Docker Desktop](https://www.docker.com/products/docker-desktop/) sur votre machine.

2. Ouvrez votre terminal et déplacez-vous à la racine du projet.

3. Exécutez la commande suivante pour construire l'image Docker :

```bash
docker-compose up --build
```

4. Ouvrez votre navigateur et accédez à l'adresse suivante : [http://localhost:8501](http://localhost:8501)

### III. Utilisez l'application en ligne

Ouvrez votre navigateur et accédez à l'adresse suivante : [sise-camp.streamlit.app](https://challenge-sise-opsie.streamlit.app)


## 🤝 Contributions
Toutes les contributions sont les bienvenues ! Voici comment vous pouvez contribuer :

Forkez le projet.
Créez votre branche de fonctionnalité (git checkout -b feature/AmazingFeature).
Commitez vos changements (git commit -m 'Add some AmazingFeature').
Pushez sur la branche (git push origin feature/AmazingFeature).
Ouvrez une Pull Request.

## 👤 Auteurs

Ce projet a été par [Yacine AYACHI](https://github.com/YacineAyachi), [Hugo COLLIN]([https://github.com/hugocollin]) , [Pierre BOURBON](https://github.com/pbrbn) et [Lucile PERBET](https://github.com/lucilecpp) dans le cadre de Challenge de Web Minning du Master SISE à l'Université Lumière Lyon 2. 



