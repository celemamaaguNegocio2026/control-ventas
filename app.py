import streamlit as st
import pandas as pd
from streamlit_barcode_reader import barcode_reader

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️")

st.title("📷 Escáner Celeste")

# URL de tu planilla
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype=str)

try:
    df = cargar_datos()
    
    st.write("### Enfocá el código de barras")
    
    # Este es el lector mágico. Solo tenés que pasar el código por la cámara.
    codigo_leido = barcode_reader(key='lector_celeste')

    if codigo_leido:
        # Mostramos el número que leyó para estar seguros
        st.success(f"✅ ¡Leído!: {codigo_leido}")
        
        # Buscamos en el Excel (limpiando espacios por las dudas)
        busqueda = str(codigo_leido).strip()
        producto = df[df['Código de Barras'] == busqueda]
        
        if not producto.empty:
            st.balloons()
            for index, row in producto.iterrows():
                st.info(f"📦 Producto: {row['Producto']}")
                st.metric("Precio", f"${row['Precio']}")
                st.metric("Stock", f"{row['Stock']} unidades")
        else:
            st.warning(f"El código {busqueda} no está cargado en el Excel.")

    st.divider()
    st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

except Exception as e:
    st.error(f"Error: {e}")
