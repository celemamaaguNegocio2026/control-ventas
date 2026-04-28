import streamlit as st
import pandas as pd
from camera_input_live import camera_input_live
from pyzbar.pyzbar import decode
from PIL import Image

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️")

st.title("📷 Escáner en Vivo")

# URL de tu planilla
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype=str)

try:
    df = cargar_datos()
    
    st.write("### Apuntá al código")
    # Cámara en vivo que no rompe la pantalla
    imagen_viva = camera_input_live()

    if imagen_viva:
        # Convertimos la imagen de la cámara a algo que el lector entienda
        img = Image.open(imagen_viva)
        codigos = decode(img)
        
        if codigos:
            codigo_leido = codigos[0].data.decode('utf-8')
            st.success(f"✅ ¡Detectado!: {codigo_leido}")
            
            # Buscamos en el Excel
            producto = df[df['Código de Barras'] == codigo_leido]
            
            if not producto.empty:
                st.balloons()
                for index, row in producto.iterrows():
                    st.subheader(f"📦 {row['Producto']}")
                    st.metric("Precio", f"${row['Precio']}")
                    st.metric("Stock", f"{row['Stock']} un.")
            else:
                st.warning(f"El código {codigo_leido} no está en tu Excel.")

    st.divider()
    st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

except Exception as e:
    st.error(f"Error: {e}")
