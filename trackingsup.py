import streamlit as st
from supabase import create_client, Client

# 1. Connexió a Supabase usant les dades de secrets.toml
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["https://cmprnzcskfzmqpbrwise.supabase.co/rest/v1/"]
    key = st.secrets["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNtcHJuemNza2Z6bXFwYnJ3aXNlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTA4NTIwMTgsImV4cCI6MjEwNjQyODAxOH0.pDnlSlg4s1T7177nwjLHCJSlTCC3Fcd5PIhcSSPcLE8"]
    return create_client(url, key)

supabase = init_supabase()

def mostrar_tracking():
    st.title("Seguiment del teu Objecte Perdut")
    st.write("Introdueix l'identificador de la teva sol·licitud o el teu correu.")

    # Entrada per a l'ID
    search_input = st.text_input("Identificador:", placeholder="Ex: REQ-101")

    if st.button("Buscar sol·licitud", type="primary"):
        if not search_input.strip():
            st.warning("⚠️ Per favor, escriu un identificador vàlid.")
            return

        with st.spinner("Comprovant identificador a la base de dades..."):
            # 2. Consultar la taula 'lost_requests'
            response = supabase.table("lost_requests") \
                .select("*") \
                .eq("id", search_input.strip()) \
                .execute()

        # 3. CONTROL D'ERROR: Si no es troba cap registre a Supabase
        if not response.data or len(response.data) == 0:
            st.error(f"L'identificador o correu **'{search_input}'** no existeix a la nostra base de dades. Si us plau, revisa-ho.")
            return  # Atura l'execució aquí per no mostrar el seguiment

        # 4. Si EXISTEIX, agafem la informació trobada
        sollicitud = response.data[0]
        st.success(f"✅ Sol·licitud trobada: `{sollicitud['id']}`")

        # Obtenir les dades de relació
        found_object_id = sollicitud.get("taking_code")
        #sack_id = sollicitud.get("sack_id")
        
        # 5. Determinar la fase del seguiment
        fase = 0
        if taking_code:
            fase = 1  # S'ha fet el match amb l'objecte trobat
            #if sack_id:
                # Opcional: consultar l'estat de la saca a la taula 'sacks'
                sack_res = supabase.table("sacks").select("status").eq("id", sack_id).execute()
            #    if sack_res.data:
                    estat_saca = sack_res.data[0].get("status")
               #     if estat_saca == "en_transit":
               #         fase = 2
                #    elif estat_saca == "arribat":
                #        fase = 3
        else:
          fase = 0

        if fase == 1:
            st.success(f"🎉 **Match trobat!** L'objecte s'ha associat amb el codi: `{taking_code}`")
        else:
            st.info("🔍 **Cercant coincidències...** Encara no s'ha trobat cap objecte assignat a la teva sol·licitud.")
        # 6. Dibuixar l'estat o línia de temps
        dibuixar_passos_tracking(fase)
