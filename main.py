"""
Ce fichier contient le code principal de l'application Streamlit.
"""

import streamlit as st

from src.app.components import (
    load_api_keys,
    stream_text,
    show_sidebar,
    create_new_research,
    generate_research_name,
)


# Configuration de la page
st.set_page_config(
    page_title="SISE Camp", page_icon="ressources/favicon.png", layout="wide"
)

# Chargement des clés API
load_api_keys()

# Mise en page personnalisée
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 50px;
            padding-bottom: 0px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

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
    # Informations sur la recherche
    current_research = st.session_state["selected_research"]
    st.write_stream(stream_text(f"**{current_research}**"))
    st.header(st.session_state["research"][current_research]["text"])

    st.info(
        "*Résultats de la recherche disponibles ultérieurement*", icon=":material/info:"
    )
    st.write("*SISE Camp peut faire des erreurs. Envisagez de vérifier les informations importantes et n'envoyez pas d'informations confidentielles.*")
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

            if len(st.session_state["research"]) < 5:
                # Barre de saisie de question
                research = st.chat_input("🔍", key="new_research")

                if research:
                    st.session_state["initial_research"] = research
                    create_new_research(research)
                    generate_research_name(research)
                    st.rerun()
            else:
                # Message d'information
                st.info(
                    "Nombre maximal de recherches atteint, "
                    "supprimez-en une pour en commencer une nouvelle",
                    icon=":material/error:",
                )
