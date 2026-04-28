import streamlit as st
import pandas as pd
from streamlit_quagga_barcode_scanner import quagga_barcode_scanner

st.set_page_config(page_title="Sistema Pro - Gestión Familiar", page_icon="🛍️")

st.title("🚀 Escáner Rápido - Celeste")

# Conexión a tu planilla
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype={'Código de Barras': str})

try:
    df = cargar_datos()
    
    menu = st.sidebar.radio("MENÚ", ["🔍 Escanear", "📦 Inventario", "💰 Nueva Venta"])

    if menu == "🔍 Escanear":
        st.subheader("Apuntá al código de barras")
        st.write("Mantené el celu firme, el sistema enfocará solo.")
        
        # Este componente es un escáner en vivo (no saca foto, lee directo)
        barcode = quagga_barcode_scanner()
        
        if barcode:
            st.success(f"✅ Detectado: {barcode}")
            producto = df[df['Código de Barras'] == str(barcode)]
            
            if not producto.empty:
                st.balloons()
                st.table(producto)
            else:
                st.warning(f"El código {barcode} no está en el Excel.")

    elif menu == "📦 Inventario":
        st.dataframe(df)

    elif menu == "💰 Nueva Venta":
        st.link_button("🚀 IR AL FORMULARIO", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

except Exception as e:
    st.error(f"Error: {e}")
