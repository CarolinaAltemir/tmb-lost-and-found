import json
import streamlit as st

st.set_page_config(
    page_title="TMB - Objectes perduts",
    page_icon="🧳",
    layout="centered"
)

# -------------------------------------------------------------
# CARREGAR DADES DES DEL JSON
# -------------------------------------------------------------
@st.cache_data
def carregar_cataleg(fitxer="catalogo.json"):
    with open(fitxer, "r", encoding="utf-8") as f:
        return json.load(f)

data = carregar_cataleg()

# Extracció dinàmica de línies des del JSON
lineas = data.get("transporte", {}).get("lineas", [])
METRO_LINES = [l["id"] for l in lineas if l.get("medio") == "metro" and l.get("activa", True)]
BUS_LINES = [l["nombre"] for l in lineas if l.get("medio") == "bus" and l.get("activa", True)]

# Mapa de categories (clau en català : nom canònic en castellà del catàleg)
CATEGORIES_TRADUCCIO = {
    "Bosses i equipatge": "Bolsas y equipaje",
    "Carteres i contenidors personals": "Carteras y pequeños contenedores personales",
    "Documentació, targetes i diners": "Documentación, tarjetas y dinero",
    "Claus i dispositius d'accés": "Llaves y dispositivos de acceso",
    "Dispositius electrònics personals": "Dispositivos electrónicos personales",
    "Àudio, fotografia i vídeo": "Audio, fotografía y vídeo",
    "Accessoris electrònics i informàtica": "Accesorios electrónicos e informática",
    "Fundes i estoigs protectors": "Fundas y estuches protectores",
    "Roba": "Ropa",
    "Complements de vestir": "Complementos de vestir",
    "Calçat": "Calzado",
    "Ulleres": "Gafas",
    "Joieria i rellotgeria convencional": "Joyería y relojes convencionales",
    "Paraigües i para-sols": "Paraguas y sombrillas",
    "Llibres, papereria i material d'estudi": "Libros, papelería y material de estudio",
    "Alimentació i recipients": "Alimentación y recipientes",
    "Higiene i cura personal": "Higiene y cuidado personal",
    "Salut i ajudes personals": "Salud y ayudas personales",
    "Nadons i puericultura": "Bebés y puericultura",
    "Joguines i jocs": "Juguetes y juegos",
    "Esport, platja i activitats a l'aire lliure": "Deporte, playa y actividades al aire libre",
    "Mobilitat personal": "Movilidad personal",
    "Instruments musicals": "Instrumentos musicales",
    "Llar, decoració i tèxtils": "Hogar, decoración y textiles",
    "Aparells elèctrics i equips voluminosos": "Aparatos eléctricos y equipos voluminosos",
    "Eines i material de treball": "Herramientas y material de trabajo",
    "Accessoris per a animals": "Accesorios para animales",
    "Paquets i embalatges": "Paquetes y embalajes",
    "Altres objectes identificables": "Otros objetos identificables",
    "No identificable": "No identificable"
}

# Subcategories per categoria des del JSON afegint les comunes ("otro", "no_identificable")
subcats_comunes = data.get("subcategorias_comunes", ["otro", "no_identificable"])
TAXONOMIA_ES = {
    cat["nombre"]: cat.get("subcategorias", []) + [s for s in subcats_comunes if s not in cat.get("subcategorias", [])]
    for cat in data.get("categorias", [])
}

COLORS_MAP = {
    "Negre": "negro", "Blanc": "blanco", "Gris": "gris", "Blau": "azul",
    "Verd": "verde", "Vermell": "rojo", "Groc": "amarillo", "Taronja": "naranja",
    "Rosa": "rosa", "Lila / Morat": "morado", "Marró": "marron",
    "Beix / Crema": "beige", "Daurat": "dorado", "Platejat": "plateado"
}

ETIQUETES_DISPONIBLES = [
    "Estat: Amb rascades / esgarrapades", "Estat: Trencat / amb esquerdes", 
    "Estat: Desgastat", "Estat: Amb taques / brut", "Estat: Peça absent o que falta",
    "Trets: Amb adhesius / enganxines", "Trets: Amb pedaç / brodat", "Trets: Amb clauer", 
    "Trets: Amb inicials o nom escrit", "Trets: Amb penjoll o adorn", "Trets: Logotip visible",
    "Material: Cuir / pell", "Material: Metall / metàl·lic", "Material: Plàstic / silicona", 
    "Material: Teixit / roba", "Material: Fusta", "Material: Vidre / ceràmica", 
    "Acabat: Brillant", "Acabat: Mate", "Acabat: Transparent / translúcid", "Acabat: Reflectant / fluorescent",
    "Estampat: Llis", "Estampat: Ratlles", "Estampat: Quadres", "Estampat: Estampat floral", 
    "Estampat: Dibuix / il·lustració", "Estampat: Multicolor",
    "Tancament: Cremallera", "Tancament: Botó / gafet", "Tancament: Velcro", "Tancament: Sivella", 
    "Element: Nanses / tirants", "Element: Butxaques", "Element: Rodes",
    "Presentació: Dins d'una funda", "Presentació: Plegat", "Presentació: En caixa / embalatge"
]

# -------------------------------------------------------------
# INTERFÍCIE DEL FORMULARI
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
cat_catala = st.selectbox("Categoria", list(CATEGORIES_TRADUCCIO.keys()))
cat_castella = CATEGORIES_TRADUCCIO[cat_catala]

# Opcions de subcategoria directes del catàleg en castellà
subcategories = TAXONOMIA_ES.get(cat_castella, ["otro", "no_identificable"])
subcategory = st.selectbox("Subcategoria", subcategories)

colors_selected = st.multiselect(
    "Colors principals (màxim 2)",
    list(COLORS_MAP.keys()),
    max_selections=data.get("max_colores", 2),
    placeholder="Tria fins a 2 colors"
)

brand = st.text_input("Marca (opcional)", max_chars=data.get("max_marca", 100))

st.divider()

st.subheader("3. Detalls i etiquetes visuals")
tags = st.multiselect("Etiquetes opcionals", ETIQUETES_DISPONIBLES)
description = st.text_area(
    "Descripció escrita / detalls addicionals",
    max_chars=data.get("max_detalles", 500),
    help="Obligatori si la subcategoria és 'otro' o 'Altres'."
)
photo = st.file_uploader("Foto (opcional)", type=["jpg", "jpeg", "png"])

st.divider()

st.subheader("4. Dades de contacte")
contact_email = st.text_input("Correu electrònic")
contact_phone = st.text_input("Telèfon")
consent = st.checkbox("Autoritzo TMB a conservar les dades i contactar-me si es troba una coincidència.")

submitted = st.button("Enviar sol·licitud", type="primary")

# -------------------------------------------------------------
# PROCESSAMENT
# -------------------------------------------------------------
if submitted:
    detalls_parts = []
    if tags:
        detalls_parts.append("Etiquetes: " + ", ".join(tags))
    if description.strip():
        detalls_parts.append(description.strip())
    detalls_finals = ". ".join(detalls_parts)

    colors_canonics = [COLORS_MAP[c] for c in colors_selected]
    linies_canoniques = [f"BUS_{l}" for l in lines] if transport == "Bus" else lines

    if not cat_catala:
        st.error("Cal indicar una categoria.")
    elif subcategory in ["otro", "Altres"] and not detalls_finals.strip():
        st.error("Per a la subcategoria 'Altres'/'otro' és obligatori afegir etiquetes o detalls.")
    elif not consent:
        st.error("Cal donar consentiment per conservar la sol·licitud.")
    else:
        registre = {
            "categoria": cat_castella,  # Desa el terme canònic del JSON
            "subcategoria": subcategory,
            "colors": colors_canonics,
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
