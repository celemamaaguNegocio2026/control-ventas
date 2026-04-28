import streamlit as st
import pandas as pd
from streamlit_zxing import st_zxing

st.set_page_config(page_title="Sistema Pro - Gestión Familiar", page_icon="🛍️")

st.title("🚀 Escáner Pro - Celeste")

# Conexión a tu planilla
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype={'Código de Barras': str})

try:
    df = cargar_datos()
    
    menu = st.sidebar.radio("MENÚ", ["🔍 Escanear Producto", "📦 Inventario Completo", "💰 Registrar Venta"])

    if menu == "🔍 Escanear Producto":
        st.subheader("📷 Apuntá al código de barras")
        st.info("Mantené el código dentro del recuadro. El sistema enfoca solo.")
        
        # Este componente es el más estable y no da errores de 'removeChild'
        resultado = st_zxing(key='scanner')
        
        if resultado:
            barcode = str(resultado)
            st.success(f"✅ Código detectado: {barcode}")
            
            # Buscamos en el Excel
            producto = df[df['Código de Barras'] == barcode]
            
            if not producto.empty:
                st.balloons()
                st.write("### ✅ Producto Encontrado:")
                st.table(producto)
            else:
                st.warning(f"El código {barcode} no está cargado en el Excel.")

    elif menu == "📦 Inventario Completo":
        st.subheader("📋 Lista de Precios y Stock")
        st.dataframe(df, use_container_width=True)

    elif menu == "💰 Registrar Venta":
        st.link_button("🚀 IR AL FORMULARIO", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

except Exception as e:
    st.error(f"Hubo un error de conexión: {e}")
