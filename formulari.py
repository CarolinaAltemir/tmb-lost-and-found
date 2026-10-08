import json
from pathlib import Path
import streamlit as st
from supabase import create_client, Client

# Configurar la pàgina AL PRINCIPI DE TOT
st.set_page_config(
    page_title="TMB - Objectes Perduts",
    page_icon="🧳",
    layout="centered"
)

# -------------------------------------------------------------
# CONNEXIÓ AMB SUPABASE (Compartida)
# -------------------------------------------------------------
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# -------------------------------------------------------------
# CARREGAR CATÀLEG (Per al formulari)
# -------------------------------------------------------------
@st.cache_data
def carregar_cataleg():
    ruta = Path(__file__).parent / "cataleg.json"
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

data = carregar_cataleg()

# Línies de transport i taxonomia
lineas = data.get("transporte", {}).get("lineas", [])
METRO_LINES = [l["id"] for l in lineas if l.get("medio") == "metro" and l.get("activa", True)]
BUS_LINES = [l["nombre"] for l in lineas if l.get("medio") == "bus" and l.get("activa", True)]

subcats_comunes = data.get("subcategories_comunes", ["Altres", "No identificable"])
TAXONOMIA = {
    cat["nombre"]: cat.get("subcategorias", []) + [s for s in subcats_comunes if s not in cat.get("subcategorias", [])]
    for cat in data.get("categorias", [])
}

# -------------------------------------------------------------
# 1. FUNCIÓ FORMULARI
# -------------------------------------------------------------
def mostrar_formulari():
    st.title("TMB - Objectes perduts")
    st.write("Formulari per registrar una reclamació d'un objecte perdut a la xarxa de TMB.")

    st.subheader("1. Dades de la pèrdua")
    loss_date = st.date_input("Dia de la pèrdua")
    transport = st.radio("Mitjà de transport", ["Metro", "Bus"], horizontal=True)

    if transport == "Metro":
        lines = st.multiselect("Línia o línies de metro", METRO_LINES, placeholder="Tria línies...")
    else:
        lines = st.multiselect("Línia o línies d'autobús", BUS_LINES, placeholder="Tria línies...")

    st.divider()

    st.subheader("2. Característiques de l'objecte")
    category = st.selectbox("Categoria", list(TAXONOMIA.keys()))
    subcategory = st.selectbox("Subcategoria", TAXONOMIA[category])

    colors_selected = st.multiselect(
        "Colors principals (màxim 2)",
        data.get("colors", []),
        max_selections=data.get("max_colors", 2),
        placeholder="Tria fins a 2 colors"
    )

    brand = st.text_input("Marca (opcional)", max_chars=data.get("max_marca", 100))

    st.divider()

    st.subheader("3. Detalls i etiquetes visuals")
    tags = st.multiselect("Etiquetes opcionals", data.get("etiquetes", []))
    description = st.text_area(
        "Descripció escrita / detalls addicionals",
        max_chars=data.get("max_detalls", 500),
        help="Obligatori si la subcategoria és 'Altres'."
    )
    photo = st.file_uploader("Foto (opcional)", type=["jpg", "jpeg", "png"])

    st.divider()

    st.subheader("4. Dades de contacte")
    contact_email = st.text_input("Correu electrònic")
    contact_phone = st.text_input("Telèfon")
    consent = st.checkbox("Autoritzo TMB a conservar les dades i contactar-me si es troba una coincidència.")

    submitted = st.button("Enviar sol·licitud", type="primary")

    if submitted:
        detalls_parts = []
        if tags:
            detalls_parts.append("Etiquetes: " + ", ".join(tags))
        if description.strip():
            detalls_parts.append(description.strip())
        detalls_finals = ". ".join(detalls_parts)

        linies_canoniques = [f"BUS_{l}" for l in lines] if transport == "Bus" else lines

        if not category:
            st.error("Cal indicar una categoria.")
        elif subcategory == "Altres" and not detalls_finals.strip():
            st.error("Per a la subcategoria 'Altres' és obligatori afegir etiquetes o descriure l'objecte.")
        elif not consent:
            st.error("Cal donar consentiment per conservar la sol·licitud.")
        else:
            registre = {
                "categoria": category,
                "subcategoria": subcategory,
                "colors": colors_selected,
                "marca": brand.strip() if brand.strip() else None,
                "detalls": detalls_finals,
                "linia": linies_canoniques,
                "dia_de_perdua": str(loss_date),
                "contacte": {
                    "email": contact_email.strip(),
                    "telefon": contact_phone.strip()
                }
            }
            st.success("Sol·licitud registrada correctament!")
            st.json(registre)

# -------------------------------------------------------------
# 2. FUNCIÓ TRACKING
# -------------------------------------------------------------
def mostrar_tracking():
    st.title("Seguiment del teu Objecte Perdut")
    st.write("Introdueix l'identificador de la teva sol·licitud.")

    search_input = st.text_input("Identificador:", placeholder="Ex: 1")

    if st.button("Buscar sol·licitud", type="primary"):
        if not search_input.strip():
            st.warning("⚠️ Per favor, escriu un identificador vàlid.")
            return

        with st.spinner("Comprovant identificador a la base de dades..."):
            response = supabase.table("lost_requests") \
                .select("*") \
                .eq("id", search_input.strip()) \
                .execute()

        if not response.data or len(response.data) == 0:
            st.error(f"❌ L'identificador **'{search_input}'** no existeix a la nostra base de dades.")
            return

        sollicitud = response.data[0]
        st.success(f"✅ Sol·licitud trobada: `{sollicitud['id']}`")

        found_object_id = sollicitud.get("taking_code")

        if found_object_id:
            fase = 1
            st.success(f"🎉 **Match trobat!** L'objecte s'ha associat amb el codi: `{found_object_id}`")
        else:
            fase = 0
            st.info("🔍 **Cercant coincidències...** Encara no s'ha trobat cap objecte assignat a la teva sol·licitud.")

# -------------------------------------------------------------
# MENÚ PRINCIPAL
# -------------------------------------------------------------
opcio = st.sidebar.radio("Navegació", ["Registrar Pèrdua", "Seguiment de Sol·licitud"])

if opcio == "Registrar Pèrdua":
    mostrar_formulari()
else:
    mostrar_tracking()
