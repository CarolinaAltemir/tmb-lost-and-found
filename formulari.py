import json
from pathlib import Path
import secrets
import re

import streamlit as st
from supabase import create_client

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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


# -------------------------------------------------------------
# LÍNIES DE TRANSPORT
# -------------------------------------------------------------
lineas = data.get("transporte", {}).get("lineas", [])

METRO_LINES = [
    l["id"]
    for l in lineas
    if l.get("medio") == "metro"
    and l.get("activa", True)
]

BUS_LINES = [
    l["nombre"]
    for l in lineas
    if l.get("medio") == "bus"
    and l.get("activa", True)
]


# -------------------------------------------------------------
# TAXONOMIA
# -------------------------------------------------------------
subcats_comunes = data.get(
    "subcategories_comunes",
    ["Altres", "No identificable"]
)

TAXONOMIA = {
    cat["nombre"]:
        cat.get("subcategorias", [])
        + [
            s
            for s in subcats_comunes
            if s not in cat.get("subcategorias", [])
        ]

    for cat in data.get("categorias", [])
}


# -------------------------------------------------------------
# FUNCIONS DE VALIDACIÓ
# -------------------------------------------------------------
def email_valid(email):
    """
    Comprova una estructura bàsica de correu:
    text@text.domini
    """
    email = email.strip()

    if len(email) < 6:
        return False

    patro = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return re.match(patro, email) is not None


def telefon_valid(telefon):
    """
    El client només ha d'escriure els 9 dígits
    del telèfon espanyol. El +34 ja s'indica
    visualment al formulari.
    """
    return telefon.isdigit() and len(telefon) == 9

# -------------------------------------------------------------
# MAIL
# -------------------------------------------------------------

def enviar_email_confirmacio(destinatari_email, tracking_code):
    """
    Envia un correu electrònic a l'usuari amb el número de seguiment.
    Mostra l'error detallat en cas de fallada.
    """
    # 1. Comprovació de Secrets
    sender_email = st.secrets.get("SMTP_EMAIL", "")
    sender_password = st.secrets.get("SMTP_PASSWORD", "")

    if not sender_email:
        st.error("❌ Error als Secrets: No s'ha trobat 'SMTP_EMAIL'. Revisa el fitxer secrets.toml.")
        return False
    if not sender_password:
        st.error("❌ Error als Secrets: No s'ha trobat 'SMTP_PASSWORD'. Revisa el fitxer secrets.toml.")
        return False

    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        app_url = "https://tmb-lost-and-found-b2tajzh2jib3hzdg8t8hsc.streamlit.app"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"TMB - Confirmació de sol·licitud ({tracking_code})"
        msg["From"] = f"TMB Objectes Perduts <{sender_email}>"
        msg["To"] = destinatari_email

        html_content = f"""
        <html>
          <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
              <h2 style="color: #d32f2f;">TMB - Registre d'Objecte Perdut</h2>
              <p>Hola,</p>
              <p>Hem rebut correctament la teva sol·licitud per a la localització d'un objecte perdut a la xarxa de TMB.</p>
              <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #d32f2f; margin: 20px 0;">
                <p style="margin: 0; font-size: 14px; color: #666666;">El teu número de seguiment és:</p>
                <h3 style="margin: 5px 0 0 0; color: #111111; font-size: 24px;">{tracking_code}</h3>
              </div>
              <p>Pots comprovar l'estat de la teva sol·licitud a la nostra plataforma:</p>
              <p style="text-align: center; margin: 30px 0;">
                <a href="{app_url}" style="background-color: #d32f2f; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                  TMB - Objectes Perduts
                </a>
              </p>
            </div>
          </body>
        </html>
        """
        msg.attach(MIMEText(html_content, "html"))

        # Connexió SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, destinatari_email, msg.as_string())
        server.quit()
        return True

    except Exception as e:
        # Mostrem l'error exacte en vermell a la pantalla
        st.error(f"❌ Error de connexió/enviament SMTP: {e}")
        return False

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
        [
            "Metro",
            "Bus",
            "Metro + Bus"
        ],
        horizontal=True,
        index=None
    )


    # Inicialitzem les dues llistes
    metro_lines_selected = []
    bus_lines_selected = []


    # ---------------------------------------------------------
    # NOMÉS METRO
    # ---------------------------------------------------------
    if transport == "Metro":

        metro_lines_selected = st.multiselect(
            "Línia o línies de metro *",
            METRO_LINES,
            max_selections=2,
            placeholder="Tria fins a 2 línies..."
        )


    # ---------------------------------------------------------
    # NOMÉS BUS
    # ---------------------------------------------------------
    elif transport == "Bus":

        bus_lines_selected = st.multiselect(
            "Línia o línies d'autobús *",
            BUS_LINES,
            max_selections=2,
            placeholder="Tria fins a 2 línies..."
        )


    # ---------------------------------------------------------
    # METRO + BUS
    # ---------------------------------------------------------
    elif transport == "Metro + Bus":

        metro_lines_selected = st.multiselect(
            "Línia de metro *",
            METRO_LINES,
            max_selections=1,
            placeholder="Tria una línia de metro..."
        )

        bus_lines_selected = st.multiselect(
            "Línia d'autobús *",
            BUS_LINES,
            max_selections=1,
            placeholder="Tria una línia d'autobús..."
        )


    # ---------------------------------------------------------
    # ENCARA NO HA TRIAT TRANSPORT
    # ---------------------------------------------------------
    else:

        st.multiselect(
            "Línia o línies *",
            [],
            placeholder="Primer selecciona el mitjà de transport",
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


    # ---------------------------------------------------------
    # SUBCATEGORIA DEPENENT DE LA CATEGORIA
    # ---------------------------------------------------------
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


    # ---------------------------------------------------------
    # COLORS
    # ---------------------------------------------------------
    colors_selected = st.multiselect(
        "Colors principals (màxim 2) *",
        data.get("colors", []),
        max_selections=data.get("max_colors", 2),
        placeholder="Tria almenys un color..."
    )


    # ---------------------------------------------------------
    # MARCA
    # ---------------------------------------------------------
    brand = st.text_input(
        "Marca",
        max_chars=data.get("max_marca", 100)
    )


    st.divider()


    # =========================================================
    # 3. DETALLS I ETIQUETES VISUALS
    # =========================================================
    st.subheader("3. Detalls i etiquetes visuals")


    # ---------------------------------------------------------
    # ETIQUETES
    # ---------------------------------------------------------
    tags = st.multiselect(
        "Etiquetes",
        data.get("etiquetes", [])
    )


    # ---------------------------------------------------------
    # DESCRIPCIÓ
    # ---------------------------------------------------------
    description = st.text_area(
        "Descripció escrita / detalls addicionals",
        max_chars=data.get("max_detalls", 500)
    )


    # ---------------------------------------------------------
    # FOTO
    # ---------------------------------------------------------
    photo = st.file_uploader(
        "Foto",
        type=[
            "jpg",
            "jpeg",
            "png"
        ]
    )


    st.divider()


    # =========================================================
    # 4. DADES DE CONTACTE
    # =========================================================
    st.subheader("4. Dades de contacte")


    # ---------------------------------------------------------
    # EMAIL
    # ---------------------------------------------------------
    contact_email = st.text_input(
        "Correu electrònic *"
    )

    contact_email_confirm = st.text_input(
        "Repeteix el correu electrònic *"
    )


    # ---------------------------------------------------------
    # TELÈFON
    # ---------------------------------------------------------
    contact_phone = st.text_input(
        "Telèfon (+34) *",
        max_chars=9,
        placeholder="Ex: 612345678"
    )


    # ---------------------------------------------------------
    # CONSENTIMENT
    # ---------------------------------------------------------
    consent = st.checkbox(
        "Autoritzo TMB a conservar les dades i "
        "contactar-me si es troba una coincidència. *"
    )


    # ---------------------------------------------------------
    # BOTÓ
    # ---------------------------------------------------------
    submitted = st.button(
        "Enviar sol·licitud",
        type="primary"
    )


    # =========================================================
    # ENVIAMENT
    # =========================================================
    if submitted:

        errors = []


        # =====================================================
        # VALIDACIÓ: DIA
        # =====================================================
        if loss_date is None:

            errors.append(
                "Cal indicar el dia de la pèrdua."
            )


        # =====================================================
        # VALIDACIÓ: TRANSPORT
        # =====================================================
        if not transport:

            errors.append(
                "Cal indicar el mitjà de transport."
            )


        # =====================================================
        # VALIDACIÓ: LÍNIES
        # =====================================================
        if transport == "Metro":

            if not metro_lines_selected:

                errors.append(
                    "Cal indicar almenys una línia de metro."
                )


        elif transport == "Bus":

            if not bus_lines_selected:

                errors.append(
                    "Cal indicar almenys una línia d'autobús."
                )


        elif transport == "Metro + Bus":

            if not metro_lines_selected:

                errors.append(
                    "Cal indicar una línia de metro."
                )

            if not bus_lines_selected:

                errors.append(
                    "Cal indicar una línia d'autobús."
                )


        # =====================================================
        # VALIDACIÓ: CATEGORIA
        # =====================================================
        if not category:

            errors.append(
                "Cal indicar una categoria."
            )


        # =====================================================
        # VALIDACIÓ: SUBCATEGORIA
        # =====================================================
        if not subcategory:

            errors.append(
                "Cal indicar una subcategoria."
            )


        # =====================================================
        # VALIDACIÓ: COLORS
        # =====================================================
        if not colors_selected:

            errors.append(
                "Cal indicar almenys un color."
            )


        # =====================================================
        # VALIDACIÓ: EMAIL
        # =====================================================
        email_1 = contact_email.strip()
        email_2 = contact_email_confirm.strip()


        if not email_1:

            errors.append(
                "Cal indicar un correu electrònic."
            )

        elif not email_valid(email_1):

            errors.append(
                "El correu electrònic no té un format vàlid."
            )


        if not email_2:

            errors.append(
                "Cal repetir el correu electrònic."
            )

        elif email_1.lower() != email_2.lower():

            errors.append(
                "Els dos correus electrònics no coincideixen."
            )


        # =====================================================
        # VALIDACIÓ: TELÈFON
        # =====================================================
        phone = contact_phone.strip()


        if not phone:

            errors.append(
                "Cal indicar un telèfon."
            )

        elif not phone.isdigit():

            errors.append(
                "El telèfon només pot contenir números."
            )

        elif len(phone) != 9:

            errors.append(
                "El telèfon ha de tenir exactament 9 dígits."
            )


        # =====================================================
        # VALIDACIÓ: CONSENTIMENT
        # =====================================================
        if not consent:

            errors.append(
                "Cal autoritzar TMB a conservar les dades "
                "i contactar en cas de coincidència."
            )


        # =====================================================
        # SI HI HA ERRORS, ATUREM L'EXECUCIÓ
        # =====================================================
        if errors:

            st.error(
                "No s'ha pogut enviar la sol·licitud. "
                "Revisa els camps obligatoris:"
            )

            for error in errors:

                st.write(
                    f"• {error}"
                )

            # No genera tracking
            # No guarda res a Supabase
            return


        # =====================================================
        # PREPARACIÓ DE LES LÍNIES
        # =====================================================

        linies_canoniques = []


        # Afegim les línies de metro
        linies_canoniques.extend(
            metro_lines_selected
        )


        # Afegim les línies de bus
        linies_canoniques.extend(
            [
                f"BUS_{l}"
                for l in bus_lines_selected
            ]
        )


        # =====================================================
        # TRACKING CODE
        # Només s'arriba aquí si tot és correcte
        # =====================================================
        tracking_code = str(
            secrets.randbelow(90_000_000)
            + 10_000_000
        )


        # =====================================================
        # REGISTRE QUE S'ENVIARÀ A SUPABASE
        # =====================================================
        registre = {

            "taking_code":
                tracking_code,

            "loss_date":
                loss_date.isoformat(),

            "transport":
                transport,

            "lines":
                linies_canoniques,

            "category":
                category,

            "subcategory":
                subcategory,

            "color":
                colors_selected,

            "brand":
                brand.strip()
                if brand.strip()
                else None,

            "description":
                description.strip()
                if description.strip()
                else None,

            # La foto encara no s'envia a Storage
            "photo_url":
                None,

            "tags":
                tags,

            # Només guardem el primer email.
            # El segon serveix exclusivament per verificar-lo.
            "contact":
                email_1,

            "contact_phone":
                phone,

            "consent":
                consent,

            "status":
                "received"
        }


        # =====================================================
        # INSERT A SUPABASE
        # =====================================================
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
            # Intentem enviar el correu de confirmació
            with st.spinner("Enviant correu de confirmació..."):
                correu_enviat = enviar_email_confirmacio(email_1, tracking_code)

            if correu_enviat:
                st.success(f"S'ha enviat un correu de confirmació a **{email_1}** amb el número de seguiment. "
                f"*(Si no el trobes a la safata d'entrada, revisa la carpeta de correu brossa o Spam)*.")

        except Exception as e:

            st.error(
                "No s'ha pogut guardar la sol·licitud."
            )

            st.write(e)
