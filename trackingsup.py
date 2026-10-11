import streamlit as st
from supabase import Client, create_client


# 1. Connexió a Supabase usant les dades de secrets.toml
@st.cache_resource
def init_supabase() -> Client:
  url = st.secrets["SUPABASE_URL"]
  key = st.secrets["SUPABASE_KEY"]
  return create_client(url, key)


supabase = init_supabase()


def mostrar_tracking():
  st.title("Seguiment del teu Objecte Perdut")
  st.write("Introdueix l'identificador de la teva sol·licitud")

  # Entrada per a l'ID
  search_input = st.text_input("Identificador:", placeholder="Ex: 70372101")

  if st.button("Buscar sol·licitud", type="primary"):
    if not search_input.strip():
      st.warning("⚠️ Per favor, escriu un identificador vàlid.")
      return

    with st.spinner("Comprovant identificador a la base de dades..."):
      # 2. Consultar la taula 'lost_requests' pel camp taking_code
      response = (
          supabase.table("lost_requests")
          .select("*")
          .eq("taking_code", search_input.strip())
          .execute()
      )

    # 3. CONTROL D'ERROR: Si no es troba cap registre a Supabase
    if not response.data or len(response.data) == 0:
      st.error(
          f"L'identificador **'{search_input}'** no existeix a la nostra base"
          " de dades. Si us plau, revisa-ho."
      )
      return

    # 4. Si EXISTEIX, agafem la informació trobada
    sollicitud = response.data[0]
    st.success(
        f"✅ Sol·licitud trobada: `{sollicitud.get('taking_code')}`"
    )

    # Obtenir el codi de match (si n'hi ha)
    found_object_id = sollicitud.get("match")

    # 5. Determinar si hi ha match actiu
    # Comprovem que no sigui None i que tampoc sigui una cadena buida o un espai
    if found_object_id and str(found_object_id).strip():
      fase = 1
      st.success(
          "🎉 **Match trobat!** L'objecte s'ha associat amb el codi:"
          f" `{found_object_id}`"
      )
    else:
      fase = 0
      st.info(
          "🔍 **Cercant coincidències...** Encara no s'ha trobat cap objecte"
          " assignat a la teva sol·licitud."
      )

    # 6. Dibuixar l'estat o línia de temps
    # dibuixar_passos_tracking(fase)
