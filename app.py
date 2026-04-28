import streamlit as st
import pandas as pd
from pyzbar.pyzbar import decode
from PIL import Image

st.set_page_config(page_title="Sistema Pro - Gestión Familiar", page_icon="📲")

st.title("📲 Sistema Inteligente - Celeste")

url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype={'Código de Barras': str})

try:
    df = cargar_datos()
    menu = st.sidebar.radio("ACCIONES", ["🏠 Inicio", "🔍 Escanear Producto", "📦 Stock Completo", "💰 Registrar Venta"])

    if menu == "🔍 Escanear Producto":
        st.subheader("📷 Escáner de Código")
        img_file = st.camera_input("Sacale una foto al código de barras")
        
        if img_file:
            img = Image.open(img_file)
            resultados = decode(img)
            
            if resultados:
                barcode = resultados[0].data.decode('utf-8')
                st.success(f"Código detectado: {barcode}")
                
                producto = df[df['Código de Barras'] == barcode]
                if not producto.empty:
                    st.balloons()
                    st.write("### ✅ Producto Encontrado:")
                    st.table(producto)
                else:
                    st.warning(f"El código {barcode} no está en el sistema.")
            else:
                st.error("No se pudo leer el código. Intentá que se vea clarito y con luz.")

    elif menu == "🏠 Inicio":
        st.write("Bienvenida al sistema mejorado.")

    elif menu == "📦 Stock Completo":
        st.dataframe(df)

    elif menu == "💰 Registrar Venta":
        st.link_button("🚀 IR AL FORMULARIO", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

except Exception as e:
    st.error(f"Error: {e}")
