import streamlit as st
import pandas as pd
from pyzbar.pyzbar import decode
from PIL import Image
import numpy as np

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️")

st.title("🛡️ Gestión Familiar - Celeste")

# --- CONEXIÓN AL EXCEL ---
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

@st.cache_data(ttl=5)
def cargar_datos():
    try:
        data = pd.read_csv(csv_url, dtype=str)
        data.columns = data.columns.str.strip()
        return data
    except:
        return None

df = cargar_datos()

if df is not None:
    st.subheader("📷 Escanear Producto")
    # Este botón abre la cámara nativa del celu, saca la foto y la sube
    archivo_foto = st.camera_input("Sacá una foto al código de barras")

    if archivo_foto:
        # Procesamos la imagen para leer las barras
        img = Image.open(archivo_foto)
        detectado = decode(img)
        
        if detectado:
            codigo_leido = detectado[0].data.decode('utf-8')
            st.success(f"✅ Código detectado: {codigo_leido}")
            
            # Buscamos en el Excel
            col_busqueda = "Codigo de barra"
            producto = df[df[col_busqueda] == codigo_leido]
            
            if not producto.empty:
                st.balloons()
                for index, row in producto.iterrows():
                    st.header(f"📦 {row['Producto']}")
                    c1, c2 = st.columns(2)
                    c1.metric("PRECIO", f"${row['Precio']}")
                    c2.metric("STOCK", f"{row['Stock']} un.")
            else:
                st.warning(f"El código {codigo_leido} no está en tu Excel.")
        else:
            st.error("No se pudo leer el código. Intentá que la foto esté bien enfocada y con luz.")

    st.divider()
    # Buscador manual por si no podés sacar la foto
    manual = st.text_input("🔍 O buscá por nombre:")
    if manual:
        res = df[df['Producto'].str.contains(manual, case=False, na=False)]
        if not res.empty:
            st.dataframe(res[['Producto', 'Precio', 'Stock']], hide_index=True)

st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
