import streamlit as st
import pandas as pd
from streamlit_barcode_canvas import barcode_canvas

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️")

st.title("📷 Escáner en Vivo")

# URL de tu planilla
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype=str)

try:
    df = cargar_datos()
    
    st.write("### Apuntá al código de barras")
    st.info("Asegurate de dar permiso a la cámara cuando el celular te pregunte.")

    # Este es el cuadrito de la cámara que escanea solo
    codigo_detectado = barcode_canvas()

    if codigo_detectado:
        st.success(f"✅ ¡Código leído!: {codigo_detectado}")
        
        # Buscamos en el Excel
        producto = df[df['Código de Barras'] == str(codigo_detectado).strip()]
        
        if not producto.empty:
            st.balloons()
            for index, row in producto.iterrows():
                st.subheader(f"📦 {row['Producto']}")
                st.metric("Precio", f"${row['Precio']}")
                st.metric("Stock", f"{row['Stock']} unidades")
        else:
            st.warning(f"El código {codigo_detectado} no está en tu lista de Excel.")

    st.divider()
    st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

except Exception as e:
    st.error(f"Error: {e}")
