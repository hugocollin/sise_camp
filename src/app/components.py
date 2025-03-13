"""
Ce fichier contient les fonctions nécessaires pour l'affichage de l'interface de l'application.
"""

import os
import time
from dotenv import find_dotenv, load_dotenv
import streamlit as st

from src.db.db_youtube import YouTubeManager
from src.llm.llm import LLM
from src.pipeline.pipeline import Pipeline


def load_api_keys():
    """
    Fonction pour charger et stocker les clés API.
    """
    # Recherche des clés API si l'application est utilisé en local
    try:
        load_dotenv(find_dotenv())
        huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        mistral_api_key = os.getenv("MISTRAL_API_KEY")
    # Sinon recherche des clés API si l'application est utilisé en ligne
    except FileNotFoundError:
        huggingface_api_key = st.secrets["HUGGINGFACE_API_KEY"]
        mistral_api_key = st.secrets["MISTRAL_API_KEY"]

    # Stockage du statut de recherche des clés API
    if huggingface_api_key and mistral_api_key:
        st.session_state["found_api_keys"] = True
        st.session_state["huggingface_api_key"] = huggingface_api_key
    else:
        st.session_state["found_api_keys"] = False


def stream_text(text: str):
    """
    Fonction pour afficher le texte progressivement.

    Args:
        text (str): Texte à afficher progressivement.
    """
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.03)


def create_new_research(research: str):
    """
    Fonction pour créer une nouvelle recherche.

    Args:
        research (str): Recherche de l'utilisateur.
    """

    # Récupération des numéros de recherche existants
    existing_numbers = [
        int(name.split(" ")[1])
        for name in st.session_state["research"].keys()
        if name.startswith("Recherche ") and name.split(" ")[1].isdigit()
    ]

    # Recherche du prochain numéro de recherche disponible
    n = 1
    while n in existing_numbers:
        n += 1

    # Création de la nouvelle recherche
    new_research_name = f"Recherche {n}"
    st.session_state["research"][new_research_name] = {"text": research}
    st.session_state["selected_research"] = new_research_name


def select_research(research_name: str):
    """
    Fonction pour sélectionner une recherche.

    Args:
        research_name (str): Nom de la recherche à sélectionner.
    """
    st.session_state["selected_research"] = research_name


def generate_research_name(research_name: str) -> str:
    """
    Fonction pour générer un nom de recherche.

    Args:
        research_name (str): Recherche de l'utilisateur.
    """
    llm = LLM()

    # 5 tentatives pour générer un nom de conversation
    for _ in range(5):
        # Génération du nom de la conversation
        research_name = llm.call_model(
            provider="mistral",
            model="mistral-large-latest",
            temperature=0.7,
            prompt_dict=[
                {
                    "role": "user",
                    "content": f"Tu es une intelligence artificielle spécialisée dans la création de nom de thématique en français. En te basant sur le texte suivant, qui est la recherche de l'utilisateur, propose une thématique d'au maximum de 30 caractères. Répond uniquement en donnant la thématique sans explication supplémentaire : {research_name}",
                }
            ],
        )

        # Nettoyage du nom de la conversation
        research_name = research_name.strip()

        # Vérification de la conformité du nom de la conversation
        if len(research_name) > 30:
            continue
        if research_name in st.session_state["research"]:
            continue

        # Changement du nom de la conversation
        st.session_state["research"][research_name] = st.session_state["research"].pop(
            list(st.session_state["research"].keys())[0]
        )
        st.session_state["selected_research"] = research_name


@st.dialog("Renommer la recherche")
def rename_research(current_name: str):
    """
    Fonction pour renommer une recherche.

    Args:
        current_name (str): Nom actuel de la recherche.
    """

    # Saisie du nouveau nom de la recherche
    new_name = st.text_input(
        "Saisissez le nouveau nom de la recherche :",
        value=current_name,
        max_chars=30,
    )

    if st.button("Enregistrer", icon=":material/save_as:", use_container_width=True):
        # Vérification de la conformité du nouveau nom
        if new_name in st.session_state["research"] and new_name != current_name:
            st.error(
                "Ce nom de recherche existe déjà, veuillez en choisir un autre.",
                icon=":material/error:",
            )
        # Enregistrement du nouveau nom
        else:
            st.session_state["research"][new_name] = st.session_state["research"].pop(
                current_name
            )
            st.session_state["selected_research"] = new_name
            if new_name != current_name:
                st.session_state["research_renamed"] = True
            st.rerun()


def show_sidebar() -> str:
    """
    Fonction pour afficher la barre latérale de l'application.

    Returns:
        str: Nom de la recherche sélectionnée.
    """

    # Initialisation des recherches
    if "research" not in st.session_state:
        st.session_state["research"] = {}

    # Initialisation de la variable d'état de renommage de recherche
    if "research_renamed" not in st.session_state:
        st.session_state["research_renamed"] = False

    with st.sidebar:
        # Logo de l'application
        st.image("ressources/icon.png", width=150)

        cols = st.columns([1, 1, 1, 2])

        # Bouton pour revenir à l'accueil
        with cols[0]:
            if st.button("", icon=":material/home:", use_container_width=True):
                st.session_state["selected_research"] = None

        # Bouton pour ajouter une vidéo YouTube
        with cols[1]:
            if st.button(
                "", icon=":material/youtube_activity:", use_container_width=True
            ):
                show_add_video_dialog()

        # Bouton pour afficher les informations sur l'application
        with cols[2]:
            if st.button("", icon=":material/info:", use_container_width=True):
                show_info_dialog()

        # Section des recherches
        st.header("Recherches")

        # Sélecteur d'espaces de discussion
        if st.session_state["research"]:
            selected_research = None
            for research_name in list(st.session_state["research"].keys()):
                btn_cols = st.columns([3, 1, 1])

                # Bouton pour sélectionner la recherche
                with btn_cols[0]:
                    st.button(
                        f":material/search: {research_name}",
                        type=(
                            "primary"
                            if research_name
                            == st.session_state.get("selected_research")
                            else "secondary"
                        ),
                        use_container_width=True,
                        on_click=select_research,
                        args=(research_name,),
                    )

                # Boutons pour renommer la recherche
                with btn_cols[1]:
                    if st.button(
                        "",
                        icon=":material/edit:",
                        key=f"rename_'{research_name}'_button",
                        use_container_width=True,
                    ):
                        rename_research(research_name)
                    if st.session_state["research_renamed"] is True:
                        st.toast(
                            "Recherche renommée avec succès !",
                            icon=":material/check_circle:",
                        )
                        st.session_state["research_renamed"] = False

                # Bouton pour supprimer la recherche
                with btn_cols[2]:
                    if st.button(
                        "",
                        icon=":material/delete:",
                        key=f"delete_'{research_name}'_button",
                        use_container_width=True,
                    ):
                        del st.session_state["research"][research_name]
                        del st.session_state[f"delete_'{research_name}'_button"]
                        if st.session_state.get("selected_research") == research_name:
                            st.session_state["selected_research"] = next(
                                iter(st.session_state["research"]), None
                            )
                        st.rerun()
            return selected_research
        else:
            # Message d'information si aucune recherche n'a été créée
            st.warning(
                "Effectuez votre première recherche via la barre de recherche",
                icon=":material/info:",
            )
            return None


@st.dialog("Ajouter une vidéo YouTube")
def show_add_video_dialog():
    """
    Fonction pour afficher la boîte de dialogue d'ajout de vidéo YouTube.
    """
    # Récupération des vidéos non traitées
    db_youtube = YouTubeManager()
    videos = db_youtube.get_pending_videos()

    if not videos:
        st.info("Toutes les vidéos ont déjà été ajoutées", icon=":material/info:")
        return

    # Création d'un mapping title / url
    video_dict = {title: url for title, url in videos}

    # Choix de la vidéo à ajouter
    selected_title = st.selectbox(
        "Choisissez une vidéo à ajouter :",
        options=list(video_dict.keys())
    )

    # Prévisualisation de la vidéo à ajouter
    youtube_url = video_dict[selected_title]
    st.video(youtube_url)

    # Récupération de la transcription
    if st.button(":material/add_circle: Ajouter la vidéo"):
        with st.status(
            "**Ajout de la vidéo en cours... Ne fermez pas la fenêtre, cela peut prendre quelques minutes !**",
            expanded=True,
        ) as status:
            st.write("Initialisation...")
            youtube_url = video_dict[selected_title]
            pipeline = Pipeline(youtube_url)

            st.write("Récupération de l'audio...")
            mp3_file = pipeline.get_mp3()

            st.write("Préparation de l'audio pour la transcription...")
            chunks = pipeline.audio_chunks(mp3_file)

            st.write("Transcription de l'audio...")
            transcription = pipeline.transcribe_audio(chunks)

            st.write("Amélioration de la transcription...")
            transcription = pipeline.transcription_enhancement(transcription)

            st.write("Création du résumé...")
            summary = pipeline.create_summary(transcription)

            st.write("Enregistrement des informations...")
            pipeline.update_video_info(transcription, summary)

            st.write("Finalisation...")
            db_youtube.mark_video_as_processed(youtube_url)
            if os.path.exists(mp3_file):
                os.remove(mp3_file)

            status.update(
                label="**La vidéo a été ajoutée avec succès ! Vous pouvez maintenant fermer la fenêtre.**",
                state="complete",
                expanded=False,
            )


@st.dialog("Informations sur l'application", width="large")
def show_info_dialog():
    """
    Fonction pour afficher les informations sur l'application.
    """

    # Crédits de l'application
    st.write(
        "*L'application est Open Source et disponible sur "
        "[GitHub](https://github.com/hugocollin/sise_camp). "
        "Celle-ci a été développée par "
        "[PERBET Lucile](https://github.com/lucilecpp), "
        "[AYACHI Yacine](https://github.com/YacineAyachi), "
        "[BOURBON Pierre](https://github.com/pbrbn) "
        "et [COLLIN Hugo](https://github.com/hugocollin), dans le cadre du Master 2 SISE.*"
    )
