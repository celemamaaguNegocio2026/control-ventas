import streamlit as st
import pandas as pd
import zxingcpp
from PIL import Image

st.set_page_config(page_title="Sistema Celeste", page_icon="🛍️")

st.title("🛡️ Sistema de Ventas Celeste")

# --- CONEXIÓN AL EXCEL ---
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

@st.cache_data(ttl=2)
def cargar_datos():
    try:
        data = pd.read_csv(csv_url, dtype=str)
        data.columns = [str(c).strip() for c in data.columns]
        return data
    except:
        return None

df = cargar_datos()

if df is not None:
    st.write("### 📷 Escanear Producto")
    
    # Usamos el componente oficial de Streamlit (el más estable)
    foto = st.camera_input("Sacale una foto al código de barras")

    if foto:
        # 1. Leemos la imagen
        img = Image.open(foto)
        
        # 2. Buscamos el código con el motor de lectura
        resultados = zxingcpp.read_barcodes(img)
        
        if resultados:
            codigo_leido = resultados[0].text
            st.success(f"✅ Código detectado: {codigo_leido}")
            
            # 3. Buscamos en el Excel
            # Buscamos la columna de códigos automáticamente
            col_cod = next((c for c in df.columns if "barra" in c.lower() or "codigo" in c.lower()), df.columns[0])
            producto = df[df[col_cod] == codigo_leido]
            
            if not producto.empty:
                st.balloons()
                for index, row in producto.iterrows():
                    # Buscamos nombre, precio y stock automáticamente
                    col_nom = next((c for c in df.columns if "prod" in c.lower() or "nombre" in c.lower()), df.columns[1])
                    col_pre = next((c for c in df.columns if "prec" in c.lower()), "Precio")
                    col_sto = next((c for c in df.columns if "stock" in c.lower()), "Stock")
                    
                    st.markdown(f"## 📦 {row[col_nom]}")
                    c1, c2 = st.columns(2)
                    c1.metric("PRECIO", f"${row.get(col_pre, '0')}")
                    c2.metric("STOCK", f"{row.get(col_sto, '0')} un.")
            else:
                st.warning(f"El código {codigo_leido} no está en tu Excel.")
        else:
            st.error("No se pudo leer el código. Intentá que la foto salga nítida y con buena luz.")

    st.divider()
    # Buscador manual por si la foto sale borrosa
    manual = st.text_input("🔍 O buscá escribiendo el nombre:")
    if manual:
        res = df[df.apply(lambda row: manual.lower() in row.astype(str).str.lower().values, axis=1)]
        if not res.empty:
            st.dataframe(res, hide_index=True)

st.divider()
st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
