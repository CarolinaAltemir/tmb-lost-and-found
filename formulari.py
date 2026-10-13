import json
from pathlib import Path
import secrets
import streamlit as st
from supabase import create_client

# -------------------------------------------------------------
# CONNEXIÓ AMB SUPABASE
# -------------------------------------------------------------
supabase_url = st.secrets["SUPABASE_URL"].strip().rstrip("/")

# Per si s'ha copiat accidentalment la URL de la REST API
if "/rest/v1" in supabase_url:
    supabase_url = supabase_url.split("/rest/v1")[0]

supabase_key = st.secrets["SUPABASE_KEY"].strip()

supabase = create_client(
    supabase_url,
    supabase_key
)

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

METRO_LINES = [
    l["id"]
    for l in lineas
    if l.get("medio") == "metro" and l.get("activa", True)
]

BUS_LINES = [
    l["nombre"]
    for l in lineas
    if l.get("medio") == "bus" and l.get("activa", True)
]

# Taxonomia directa del JSON
subcats_comunes = data.get(
    "subcategories_comunes",
    ["Altres", "No identificable"]
)

TAXONOMIA = {
    cat["nombre"]:
        cat.get("subcategorias", [])
        + [
            s for s in subcats_comunes
            if s not in cat.get("subcategorias", [])
        ]

    for cat in data.get("categorias", [])
}


# -------------------------------------------------------------
# FORMULARI
# -------------------------------------------------------------
def mostrar_formulari():

    st.title("TMB - Objectes perduts")

    st.write(
        "Formulari per registrar una reclamació "
        "d'un objecte perdut a la xarxa de TMB."
    )

    st.caption("* Camps obligatoris")

    # =========================================================
    # 1. DADES DE LA PÈRDUA
    # =========================================================
    st.subheader("1. Dades de la pèrdua")

    loss_date = st.date_input(
        "Dia de la pèrdua *",
        value=None
    )

    transport = st.radio(
        "Mitjà de transport *",
        ["Metro", "Bus"],
        horizontal=True,
        index=None
    )

    if transport == "Metro":

        lines = st.multiselect(
            "Línia o línies de metro *",
            METRO_LINES,
            placeholder="Tria almenys una línia..."
        )

    elif transport == "Bus":

        lines = st.multiselect(
            "Línia o línies d'autobús *",
            BUS_LINES,
            placeholder="Tria almenys una línia..."
        )

    else:

        lines = []

        st.multiselect(
            "Línia o línies *",
            [],
            placeholder="Primer selecciona Metro o Bus",
            disabled=True
        )

    st.divider()

    # =========================================================
    # 2. CARACTERÍSTIQUES DE L'OBJECTE
    # =========================================================
    st.subheader("2. Característiques de l'objecte")

    category = st.selectbox(
        "Categoria *",
        list(TAXONOMIA.keys()),
        index=None,
        placeholder="Tria una categoria..."
    )

    if category:

        subcategory = st.selectbox(
            "Subcategoria *",
            TAXONOMIA[category],
            index=None,
            placeholder="Tria una subcategoria..."
        )

    else:

        subcategory = None

        st.selectbox(
            "Subcategoria *",
            [],
            index=None,
            placeholder="Primer selecciona una categoria",
            disabled=True
        )

    colors_selected = st.multiselect(
        "Colors principals (màxim 2) *",
        data.get("colors", []),
        max_selections=data.get("max_colors", 2),
        placeholder="Tria almenys un color..."
    )

    brand = st.text_input(
        "Marca",
        max_chars=data.get("max_marca", 100)
    )

    st.divider()

    # =========================================================
    # 3. DETALLS I ETIQUETES VISUALS
    # =========================================================
    st.subheader("3. Detalls i etiquetes visuals")

    tags = st.multiselect(
        "Etiquetes",
        data.get("etiquetes", [])
    )

    description = st.text_area(
        "Descripció escrita / detalls addicionals",
        max_chars=data.get("max_detalls", 500)
    )

    photo = st.file_uploader(
        "Foto",
        type=["jpg", "jpeg", "png"]
    )

    st.divider()

    # =========================================================
    # 4. DADES DE CONTACTE
    # =========================================================
    st.subheader("4. Dades de contacte")

    contact_email = st.text_input(
        "Correu electrònic *"
    )

    contact_phone = st.text_input(
        "Telèfon *"
    )

    consent = st.checkbox(
        "Autoritzo TMB a conservar les dades i "
        "contactar-me si es troba una coincidència. *"
    )

    submitted = st.button(
        "Enviar sol·licitud",
        type="primary"
    )

    # =========================================================
    # ENVIAMENT
    # =========================================================
    if submitted:

        # -----------------------------------------------------
        # VALIDACIÓ DELS CAMPS OBLIGATORIS
        # -----------------------------------------------------
        errors = []

        if loss_date is None:
            errors.append(
                "Cal indicar el dia de la pèrdua."
            )

        if not transport:
            errors.append(
                "Cal indicar el mitjà de transport."
            )

        if not lines:
            errors.append(
                "Cal indicar almenys una línia."
            )

        if not category:
            errors.append(
                "Cal indicar una categoria."
            )

        if not subcategory:
            errors.append(
                "Cal indicar una subcategoria."
            )

        if not colors_selected:
            errors.append(
                "Cal indicar almenys un color."
            )

        if not contact_email.strip():
            errors.append(
                "Cal indicar un correu electrònic."
            )

        if not contact_phone.strip():
            errors.append(
                "Cal indicar un telèfon."
            )

        if not consent:
            errors.append(
                "Cal autoritzar TMB a conservar les dades "
                "i contactar en cas de coincidència."
            )

        # -----------------------------------------------------
        # SI HI HA ERRORS, NO CONTINUEM
        # -----------------------------------------------------
        if errors:

            st.error(
                "No s'ha pogut enviar la sol·licitud. "
                "Revisa els camps obligatoris:"
            )

            for error in errors:
                st.write(f"• {error}")

            # IMPORTANT:
            # No genera tracking
            # No guarda res a Supabase
            return

        # -----------------------------------------------------
        # PREPARACIÓ DE LES DADES
        # -----------------------------------------------------
        linies_canoniques = (
            [f"BUS_{l}" for l in lines]
            if transport == "Bus"
            else lines
        )

        # -----------------------------------------------------
        # TRACKING CODE
        # Només es genera quan tot és correcte
        # -----------------------------------------------------
        tracking_code = str(
            secrets.randbelow(90_000_000)
            + 10_000_000
        )

        # -----------------------------------------------------
        # REGISTRE QUE S'ENVIARÀ A SUPABASE
        # -----------------------------------------------------
        registre = {

            "taking_code": tracking_code,

            "loss_date": loss_date.isoformat(),

            "transport": transport,

            "lines": linies_canoniques,

            "category": category,

            "subcategory": subcategory,

            "color": colors_selected,

            "brand": (
                brand.strip()
                if brand.strip()
                else None
            ),

            "description": (
                description.strip()
                if description.strip()
                else None
            ),

            # La foto encara no s'envia a Storage
            "photo_url": None,

            "tags": tags,

            "contact": contact_email.strip(),

            "contact_phone": contact_phone.strip(),

            "consent": consent,

            "status": "received"
        }

        # -----------------------------------------------------
        # INSERT A SUPABASE
        # -----------------------------------------------------
        try:

            supabase.table(
                "lost_requests"
            ).insert(
                registre
            ).execute()

            st.success(
                "Sol·licitud registrada correctament!"
            )

            st.info(
                f"El teu número de seguiment és: "
                f"**{tracking_code}**"
            )

        except Exception as e:

            st.error(
                "No s'ha pogut guardar la sol·licitud."
            )

            st.write(e)
