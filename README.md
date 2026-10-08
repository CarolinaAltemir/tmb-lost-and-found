
1. Crear repositorio GitHub vacío y añadir a los tres.
2. Crear app.py y hacer que aparezca vuestro formulario con Streamlit.
3. Crear proyecto Supabase.
4. Crear las tablas de la base de datos con schema.sql.
5. Introducir manualmente categorías, subcategorías, colores y líneas.
6. Conectar Python con Supabase.
7. Hacer que Enviar solicitud cree una fila en lost_requests.
8. Añadir las relaciones request_lines y request_colors.
9. Crear tags + request_tags.
10. Crear tag_extractor.py para generar las primeras etiquetas.
11. Subir una fotografía.
12. Desplegar la web desde GitHub.
13. Crear 50-100 objetos ficticios y probar que todo se guarda correctamente.
14. Después empezar el matching con el otro grupo.


Como se conectan:

Usuario rellena formulario
        ↓
Pulsa "Enviar"
        ↓
app.py recoge esos valores
        ↓
Python los manda a Supabase
        ↓
Supabase crea una nueva fila en lost_requests
