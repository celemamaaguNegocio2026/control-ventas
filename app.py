import streamlit as st
import pandas as pd
from streamlit_barcode_scanner import st_barcode_scanner

# Configuración visual
st.set_page_config(page_title="Sistema Pro - Gestión Familiar", page_icon="📲")

st.title("📲 Sistema Inteligente - Celeste")

# URL de tu planilla
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")
url_formulario = "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform?usp=sf_link"

def cargar_datos():
    # Forzamos la lectura de los códigos de barra como texto para que no borre los ceros
    return pd.read_csv(csv_url, dtype={'Código de Barras': str})

try:
    df = cargar_datos()
    
    menu = st.sidebar.radio("ACCIONES", ["🏠 Inicio", "🔍 Escanear Producto", "📦 Stock Completo", "💰 Registrar Venta"])

    if menu == "🏠 Inicio":
        st.subheader(f"¡Hola Celeste!")
        st.write("El sistema ya reconoce tus códigos de barra. ¿Qué querés hacer hoy?")
        
    elif menu == "🔍 Escanear Producto":
        st.subheader("📷 Escáner de Cámara")
        st.write("Apuntá al código de barras del producto:")
        
        # Aquí se activa la cámara
        barcode = st_barcode_scanner()
        
        if barcode:
            st.success(f"Código detectado: {barcode}")
            
            # Buscamos el producto en tu Excel
            # Asegurate que en tu Excel la columna se llame exactamente: Código de Barras
            if 'Código de Barras' in df.columns:
                producto_encontrado = df[df['Código de Barras'] == barcode]
                
                if not producto_encontrado.empty:
                    st.balloons()
                    st.write("### ✅ Producto Encontrado:")
                    st.table(producto_encontrado)
                else:
                    st.warning("El código no está en la planilla. ¿Querés agregarlo?")
            else:
                st.error("No encuentro la columna 'Código de Barras' en tu Excel.")

    elif menu == "📦 Stock Completo":
        st.subheader("📋 Lista de Precios e Inventario")
        st.dataframe(df, use_container_width=True)

    elif menu == "💰 Registrar Venta":
        st.subheader("💸 Cargar Venta Nueva")
        st.link_button("🚀 IR AL FORMULARIO DE VENTA", url_formulario, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
