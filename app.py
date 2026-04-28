import streamlit as st
import pandas as pd

st.title("🛍️ Gestión Familiar - Conexión Directa")

# Link directo (Cambiamos el método para no usar Secrets)
url = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

try:
    df = pd.read_csv(csv_url)
    st.success("✅ ¡CONECTADO DIRECTAMENTE!")
    st.write("Datos de tu planilla:")
    st.dataframe(df)
except Exception as e:
    st.error("No se pudo leer la planilla. Asegurate de que esté en 'Cualquier persona con el enlace puede leer'.")
