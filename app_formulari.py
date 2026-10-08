import json
from pathlib import Path
import secrets
import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="TMB - Objectes perduts",
    page_icon="🧳",
    layout="centered"
)
# -------------------------------------------------------------
# CONNEXIÓ AMB SUPABASE
# -------------------------------------------------------------
@st.cache_resource
def connectar_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = connectar_supabase()
# -------------------------------------------------------------
# CARREGAR DADES
# -------------------------------------------------------------
@st.cache_data
def carregar_cataleg():
    ruta = Path(__file__).parent / "cataleg.json"
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

data = carregar_cataleg()

# Línies de transport
lineas = data.get("transporte", {}).get("lineas", [])
METRO_LINES = [l["id"] for l in lineas if l.get("medio") == "metro" and l.get("activa", True)]
BUS_LINES = [l["nombre"] for l in lineas if l.get("medio") == "bus" and l.get("activa", True)]

# Taxonomia directa del JSON
subcats_comunes = data.get("subcategories_comunes", ["Altres", "No identificable"])
TAXONOMIA = {
    cat["nombre"]: cat.get("subcategorias", []) + [s for s in subcats_comunes if s not in cat.get("subcategorias", [])]
    for cat in data.get("categorias", [])
}

# -------------------------------------------------------------
# FORMULARI
# -------------------------------------------------------------
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

# -------------------------------------------------------------
# ENVIAMENT
# -------------------------------------------------------------
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
    # Generem un codi de seguiment aleatori de 8 dígits
    tracking_code = str(
        secrets.randbelow(90_000_000) + 10_000_000
    )

    # Preparem les dades amb els mateixos noms
    # que les columnes de Supabase
    registre = {
        "tracking_code": tracking_code,
        "loss_date": loss_date.isoformat(),
        "transport": transport,
        "lines": linies_canoniques,
        "category": cat_castella,
        "subcategory": subcategory,
        "colors": colors_canonics,
        "brand": brand.strip() if brand.strip() else None,
        "description": description.strip() if description.strip() else None,
        "photo_path": None,
        "tags": tags,
        "contact_email": contact_email.strip(),
        "contact_phone": contact_phone.strip(),
        "consent": consent,
        "status": "received"
    }

    try:
        supabase.table("lost_requests").insert(registre).execute()

        st.success("Sol·licitud registrada correctament!")

        st.info(
            f"El teu número de seguiment és: **{tracking_code}**"
        )

    except Exception as e:
        st.error("No s'ha pogut guardar la sol·licitud.")
        st.write(e)
