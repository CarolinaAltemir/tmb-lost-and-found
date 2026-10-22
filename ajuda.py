import base64
from pathlib import Path
import streamlit as st

def mostrar_ajuda():
    st.subheader("ℹ️ Com funciona el servei d'Objectes Perduts?")
    st.write("Consulta el recorregut d'un objecte perdut des que es perd fins que es retorna al client.")

    # Ruta del PDF de la infografia
    ruta_pdf = Path(__file__).parent / "App Steps and FAQ Poster - Imatge.png"

    if ruta_pdf.exists():
        with open(ruta_pdf, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
        
        # Visor del PDF incrustat a la pàgina
        pdf_html = f'''
            <iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0&navpanes=0&scrollbar=0" 
                    width="100%" 
                    height="800" 
                    type="application/pdf"
                    style="border: 1px solid #e0e0e0; border-radius: 8px;">
            </iframe>
        '''
        st.markdown(pdf_html, unsafe_allow_html=True)
    else:
        st.error(f"No s'ha trobat el fitxer PDF a la ruta: {ruta_pdf}")
