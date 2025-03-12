import streamlit as st

from src.app.components import load_api_keys
from src.transcriptor.transcriptor import Transcriptor

st.title("Transcription YouTube")

# Chargement des clés API
load_api_keys()

youtube_url = st.text_input("Entrez le lien YouTube")

if st.button("Transcrire"):
    with st.spinner("Téléchargement et conversion..."):
        transcriptor = Transcriptor(youtube_url)
    with st.spinner("Transcription de l'audio..."):
        transcription = transcriptor.get_transcription()
    st.success("Transcription terminée !")
    st.write(transcription)