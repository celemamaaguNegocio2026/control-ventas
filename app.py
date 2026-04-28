import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Configuración de la pestaña del navegador
st.set_page_config(page_title="App de Celeste", page_icon="🚀")

# Título principal en la pantalla
st.title("🛍️ Gestión Familiar - ¡FUNCIONA!")

# Conexión con tu planilla de Google
url = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# Intentar leer los datos del inventario
try:
    df = conn.read(spreadsheet=url, worksheet="Inventario")
    st.success("✅ ¡Conectado a la planilla con éxito, Celeste!")
    st.subheader("Datos actuales en el Inventario:")
    st.dataframe(df)
except Exception as e:
    st.error("Todavía falta configurar los 'Secrets' en la página de Streamlit")
    st.info("Copiá el link de tu planilla en la configuración de la App.")
