import streamlit as st

st.title("TMB - Objectes perduts")
st.write("Formulari per registrar una reclamació d'un objecte perdut.")



    # -------------------------
    # DADES DE LA PÈRDUA
    # -------------------------

    loss_date = st.date_input(
        "Dia de pèrdua"
    )

    transport = st.radio(
        "Mitjà de transport",
        ["Metro", "Bus"]
    )

    if transport == "Metro":
        lines = st.multiselect(
            "Línia o línies",
            [
                "L1", "L2", "L3", "L4", "L5",
                "L9N", "L9S", "L10N", "L10S", "L11"
            ]
        )
    else:
        lines = st.multiselect(
            "Línia o línies de bus",
            [
                "H6", "H8", "H10", "H12",
                "V7", "V9", "V11",
                "D20", "D40"
            ]
        )

    # anonymity_level = st.selectbox(
     #   "Grau d'anonimat",
      #   [
       #      "Identificat",
       #      "Anònim"
       #  ]
    # )

with st.form("lost_object_form"):
    
    # -------------------------
    # CARACTERÍSTIQUES OBJECTE
    # -------------------------

    category = st.selectbox(
        "Categoria",
        [
            "Electrònica",
            "Bosses i motxilles",
            "Roba",
            "Documents",
            "Claus",
            "Accessoris",
            "Altres"
        ]
    )

    # Subcategories depend on category
    subcategories = {

        "Electrònica": [
            "Telèfon mòbil",
            "Auriculars",
            "Ordinador",
            "Tauleta",
            "Carregador"
        ],

        "Bosses i motxilles": [
            "Motxilla",
            "Bossa",
            "Maleta",
            "Cartera"
        ],

        "Roba": [
            "Jaqueta",
            "Abric",
            "Jersei",
            "Bufanda",
            "Sabates"
        ],

        "Documents": [
            "DNI / NIE",
            "Passaport",
            "Carnet",
            "Targeta"
        ],

        "Claus": [
            "Claus",
            "Clauer"
        ],

        "Accessoris": [
            "Ulleres",
            "Rellotge",
            "Joies",
            "Paraigua"
        ],

        "Altres": [
            "Altres"
        ]
    }

    subcategory = st.selectbox(
        "Subcategoria",
        subcategories[category]
    )

    colors = st.multiselect(
        "Colors bàsics (màxim 2)",
        [
            "Negre",
            "Blanc",
            "Gris",
            "Blau",
            "Vermell",
            "Verd",
            "Groc",
            "Marró",
            "Rosa",
            "Taronja",
            "Lila"
        ],
        max_selections=2
    )

    brand = st.text_input(
        "Marca (opcional)"
    )

    description = st.text_area(
        "Descripció escrita (opcional)"
    )

    photo = st.file_uploader(
        "Foto (opcional)",
        type=["jpg", "jpeg", "png"]
    )

    # -------------------------
    # ETIQUETES
    # -------------------------

    tags = st.multiselect(
        "Etiquetes",
        [
            "Ratllat",
            "Trencat",
            "Amb adhesius",
            "Amb clauer",
            "Amb funda",
            "Amb inicials",
            "Estampat",
            "Metàl·lic",
            "Pell",
            "Sense marca visible"
        ]
    )

    # -------------------------
    # DADES DE CONTACTE
    # -------------------------

    contact_email = st.text_input(
        "Correu electrònic"
    )

    contact_phone = st.text_input(
        "Telèfon"
    )

    consent = st.checkbox(
        "Autoritzo TMB a conservar les dades i contactar-me si es troba una coincidència."
    )

    submitted = st.form_submit_button(
        "Enviar sol·licitud"
    )


if submitted:

    if not category:
        st.error("Cal indicar una categoria.")

    elif not consent:
        st.error("Cal donar consentiment per conservar la sol·licitud.")

    else:
        st.success("Sol·licitud registrada correctament.")
