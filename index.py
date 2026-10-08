import streamlit as st

# Importar funciones de otros ficheros .py
from app2form import mostrar_formulari
from tracking import mostrar_tracking

if "pagina" not in st.session_state:
    st.session_state["pagina"] = "inici"

if st.session_state["pagina"] == "inici":
    st.title("🚌 TMB - Objectes Perduts")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Anar al Formulari", use_container_width=True):
            st.session_state["pagina"] = "app2form"
            st.rerun()
            
    with col2:
        if st.button("📍 Anar al Tracking", use_container_width=True):
            st.session_state["pagina"] = "tracking"
            st.rerun()

elif st.session_state["pagina"] == "app2form":
    if st.button("⬅️ Tornar a l'Inici"):
        st.session_state["pagina"] = "inici"
        st.rerun()
    mostrar_formulari()  # Cridem la funció del fitxer formulari.py

elif st.session_state["pagina"] == "tracking":
    if st.button("⬅️ Tornar a l'Inici"):
        st.session_state["pagina"] = "inici"
        st.rerun()
    mostrar_tracking()  # Cridem la funció del fitxer tracking.py
