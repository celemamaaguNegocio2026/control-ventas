import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestión Celeste", page_icon="🛍️")

st.title("🛍️ Gestión Familiar - Celeste")

# URL de tu planilla
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype={'Código de Barras': str})

try:
    df = cargar_datos()
    
    # OPCIÓN 1: LA CÁMARA (Para ver el producto)
    st.subheader("📷 Escáner Visual")
    foto = st.camera_input("Sacá una foto al producto si querés verlo grande")
    
    st.divider()

    # OPCIÓN 2: EL BUSCADOR (Lo más confiable)
    st.subheader("🔍 Buscador de Precios")
    busqueda = st.text_input("Escribí el nombre o pegá el código aquí:")

    if busqueda:
        # Buscamos en el Excel
        resultado = df[
            (df['Producto'].str.contains(busqueda, case=False, na=False)) | 
            (df['Código de Barras'] == busqueda)
        ]
        
        if not resultado.empty:
            st.success("¡Encontrado!")
            for index, row in resultado.iterrows():
                st.write(f"### {row['Producto']}")
                c1, c2 = st.columns(2)
                c1.metric("Precio", f"${row['Precio']}")
                c2.metric("Stock", f"{row['Stock']} un.")
                st.divider()
        else:
            st.warning("No se encontró ese producto en el Excel.")

    st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

except Exception as e:
    st.error(f"Error: {e}")
