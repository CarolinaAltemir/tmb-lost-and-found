import streamlit as st

# Importar funciones de otros ficheros .py
from formulari import mostrar_formulari
from trackingsup import mostrar_tracking

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "inici"

if st.session_state["pagina"] == "inici":
    st.title("TMB - Objectes Perduts")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Anar al Formulari", use_container_width=True):
            st.session_state["pagina"] = "formulari"
            st.rerun()
            
    with col2:
        if st.button("Anar al Tracking", use_container_width=True):
            st.session_state["pagina"] = "trackingsup"
            st.rerun()

elif st.session_state["pagina"] == "formulari":
    if st.button("⬅️ Tornar a l'Inici"):
        st.session_state["pagina"] = "inici"
        st.rerun()
    mostrar_formulari()  # Cridem la funció del fitxer formulari.py

elif st.session_state["pagina"] == "trackingsup":
    if st.button("⬅️ Tornar a l'Inici"):
        st.session_state["pagina"] = "inici"
        st.rerun()
    mostrar_tracking()  # Cridem la funció del fitxer tracking.py
