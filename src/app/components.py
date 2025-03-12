import os
from dotenv import find_dotenv, load_dotenv
import streamlit as st

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
    if huggingface_api_key and mistral_api_key :
        st.session_state["found_api_keys"] = True
        st.session_state["huggingface_api_key"] = huggingface_api_key
    else:
        st.session_state["found_api_keys"] = False
