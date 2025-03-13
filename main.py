"""
Ce fichier contient le code principal de l'application Streamlit.
"""

import streamlit as st

from src.app.components import (
    load_api_keys,
    show_research,
    show_sidebar,
    create_new_research,
    generate_research_name,
)


# Configuration de la page
st.set_page_config(
    page_title="SISE Camp", page_icon="ressources/favicon.png", layout="wide"
)

# Mise en page personnalisée
st.html(
    """
    <style>
        .block-container {
            padding-top: 0px;
            padding-bottom: 0px;
            animation: fadeIn 1s ease-in;
        }
        
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
        
        .stButton button {
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .stButton button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        
        .stImage img {
            transition: transform 0.5s;
        }
        
        .stImage img:hover {
            transform: scale(1.05);
        }
    </style>
    """
)

# Chargement des clés API
load_api_keys()

# Initialiser l'état de recherche en cours si nécessaire
if "research_in_progress" not in st.session_state:
    st.session_state["research_in_progress"] = False

# Affichage de la barre latérale
SELECTED_RESEARCH = show_sidebar()

# Stockage de la recherche sélectionnée
if SELECTED_RESEARCH:
    st.session_state["selected_research"] = SELECTED_RESEARCH
elif "selected_research" not in st.session_state and SELECTED_RESEARCH:
    st.session_state["selected_research"] = SELECTED_RESEARCH

# Affichage de la recherche sélectionnée
if (
    "selected_research" in st.session_state
    and st.session_state["selected_research"] is not None
):
    # Résultats de la recherche
    current_research = st.session_state["selected_research"]
    show_research(current_research)
else:
    st.container(height=200, border=False)
    with st.container():
        # Affichage si une ou plusieurs clés d'API sont introuvables
        if st.session_state["found_api_keys"] is False:
            # Message d'erreur
            st.error(
                "**Application indisponible :** "
                "Une ou plusieurs clés d'API sont introuvables.",
                icon=":material/error:",
            )
        else:
            # Logo de l'application
            cols = st.columns([1, 2.5, 1])
            with cols[1]:
                st.image("ressources/logo.png", use_container_width=True)

            cols = st.columns([1, 5, 1])
            with cols[1]:
                if len(st.session_state["researchs"]) < 5:
                    if st.session_state["research_in_progress"]:
                        # Animation de recherche
                        cols = st.columns([1, 1, 1])
                        with cols[1]:
                            st.image("ressources/research.gif", use_container_width=True)
                    else:
                        # Barre de saisie de question
                        research = st.chat_input("🔍", key="new_research")

                        if research:
                            # Activer l'état de recherche en cours
                            st.session_state["research_in_progress"] = True
                            st.session_state["initial_research"] = research
                            st.rerun()

                    # Traitement de la recherche si elle existe et qu'elle est en cours
                    if st.session_state["research_in_progress"] and "initial_research" in st.session_state:
                        research = st.session_state["initial_research"]
                        create_new_research(research)
                        generate_research_name(research)

                        # Réinitialisation de l'état de recherche
                        st.session_state["research_in_progress"] = False
                        del st.session_state["initial_research"]
                        st.rerun()
                else:
                    # Message d'information
                    st.warning(
                        "Nombre maximal de recherches atteint, "
                        "supprimez-en une pour en commencer une nouvelle",
                        icon=":material/error:",
                    )
