from pathlib import Path
import streamlit as st

def mostrar_ajuda():
    st.subheader("Com funciona el servei d'Objectes Perduts?")
    st.write("Consulta el recorregut d'un objecte perdut des que es perd fins que es retorna al client.")

    # Ruta de la imatge de la infografia
    ruta_imatge = Path(__file__).parent / "App Steps and FAQ Poster Bo.png"

    if ruta_imatge.exists():
        st.image(
            str(ruta_imatge),
            caption="Infografia del procés de gestió d'objectes perduts a TMB",
            use_container_width=True
        )
    else:
        st.error(f"No s'ha trobat la imatge a la ruta: {ruta_imatge}")
