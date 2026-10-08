import streamlit as st

def render_stepper(fase_actual):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if fase_actual >= 1:
            st.markdown("### 🟢 **1. Match Trobat**")
            st.caption("Objecte assignat")
        else:
            st.markdown("### ⚪ **1. En Cerca**")
            st.caption("Buscant coincidències...")

    with col2:
        if fase_actual >= 2:
            st.markdown("### 🟢 **2. En Trànsit**")
            st.caption("Saca enviada")
        elif fase_actual == 1:
            st.markdown("### 🟡 **2. En Trànsit**")
            st.caption("Pendent d'enviament")
        else:
            st.markdown("### ⚪ **2. En Trànsit**")
            st.caption("Pendent")

    with col3:
        if fase_actual == 3:
            st.markdown("### 🟢 **3. Punt de Recollida**")
            st.caption("Arribat a Sagrada Família")
        else:
            st.markdown("### ⚪ **3. Punt de Recollida**")
            st.caption("Sagrada Família")

    percentatge = {0: 0, 1: 33, 2: 66, 3: 100}[fase_actual]
    st.progress(percentatge)


def mostrar_tracking():
    st.title("📍 Seguiment del teu Objecte Perdut")
    st.write("Introdueix el teu correu per comprovar l'estat de la teva sol·licitud.")

    st.divider()

    search_query = st.text_input("Correu electrònic o ID de la sol·licitud:")

    if st.button("Buscar") or search_query:
        st.divider()
        
        # -------------------------------------------------------------
        # SIMULACIÓ DE DADES DE SUPABASE
        # -------------------------------------------------------------
        # Quan connecteu Supabase, llegireu la taula de la sol·licitud i de la saca:
        
        sollicitud = {
            "id": "REQ-1024",
            "found_object_id": "OBJ-5542",  # Si és None -> No hi ha match (Fase 0)
            "sack_id": "SACA-03"
        }
        
        # Estat de la saca trobat a la taula de saques:
        # opcions d'estat: 'en_preparacio', 'en_transit', 'arribat'
        estat_saca = "en_transit" 

        # DETERMINAR LA FASE
        if not sollicitud["found_object_id"]:
            fase = 0
        elif estat_saca == "en_transit":
            fase = 2
        elif estat_saca == "arribat":
            fase = 3
        else:
            fase = 1  # Té match però la saca encara està en preparació

        # DIBUIXAR INTERFÍCIE
        st.subheader(f"📦 Sol·licitud: {sollicitud['id']}")
        if sollicitud["found_object_id"]:
            st.caption(f"ID d'objecte trobat: `{sollicitud['found_object_id']}` | Assignat a la saca: `{sollicitud['sack_id']}`")

        st.write("---")
        render_stepper(fase)
        st.write("---")

        if fase == 0:
            st.info("🔍 Estem buscant el teu objecte a la nostra base de dades.")
        elif fase == 1:
            st.success("🎉 Hem trobat el teu objecte! Està empaquetat a la saca esperant ser enviat.")
        elif fase == 2:
            st.warning("🚚 La saca amb el teu objecte està actualment en trànsit cap a Sagrada Família.")
        elif fase == 3:
            st.balloons()
            st.success("📍 La saca ha arribat a Sagrada Família! Ja pots passar a recollir el teu objecte.")
