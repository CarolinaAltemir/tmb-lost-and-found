import streamlit as st

def mostrar_tracking():
    st.title("📍 Tracking d'Objectes Perduts")
    st.write("Consulta l'estat de la teva sol·licitud o cerca si un objecte ha estat trobat.")

    st.divider()

    # Camp per introduir el codi de seguiment o correu
    tracking_id = st.text_input(
        "Codi de la sol·licitud o correu electrònic", 
        placeholder="Ex: TMB-123456 o usuari@prova.cat"
    )

    if st.button("Buscar sol·licitud", type="primary"):
        if tracking_id:
            st.info(f"🔎 Cercant informació per a la referència: **{tracking_id}**...")
            
            # Dades de prova (més endavant es connectarà a Supabase)
            st.success("✅ Sol·licitud trobada a la base de dades (Dades de prova)")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(label="Estat", value="En cerca")
                st.write("**Data de registre:** 08/10/2026")
            with col2:
                st.metric(label="Coincidències", value="0 trobades")
                st.write("**Categoria:** Electrònica")
                
        else:
            st.warning("⚠️ Per favor, introdueix un codi de referència o un correu vàlid.")
