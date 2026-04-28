import streamlit as st
import pandas as pd
import cv2
import numpy as np
from PIL import Image

st.set_page_config(page_title="Sistema Pro - Gestión Familiar", page_icon="📲")

st.title("📷 Escáner Celeste")

# Conexión a tu planilla
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype={'Código de Barras': str})

try:
    df = cargar_datos()
    
    # Menú lateral
    menu = st.sidebar.radio("MENÚ", ["🔍 Escanear Producto", "📦 Stock Completo", "💰 Registrar Venta"])

    if menu == "🔍 Escanear Producto":
        st.subheader("Sacale una foto al código")
        
        # Esto abre la cámara del celu directamente
        img_file = st.camera_input("Enfocá bien el código de barras")
        
        if img_file:
            # Convertimos la foto para que el sistema la entienda
            file_bytes = np.asarray(bytearray(img_file.read()), dtype=np.uint8)
            opencv_image = cv2.imdecode(file_bytes, 1)
            
            # Usamos el detector de códigos de OpenCV
            detector = cv2.barcode.BarcodeDetector()
            ok, decoded_info, decoded_type, points = detector.detectAndDecode(opencv_image)
            
            if ok and decoded_info[0]:
                barcode = str(decoded_info[0])
                st.success(f"✅ Código detectado: {barcode}")
                
                # Buscamos en el Excel
                producto = df[df['Código de Barras'] == barcode]
                
                if not producto.empty:
                    st.balloons()
                    st.write("### Información del Producto:")
                    st.table(producto)
                else:
                    st.warning(f"El código {barcode} no está en tu lista de Excel.")
            else:
                st.error("❌ No se pudo leer. Intentá que el código esté bien derecho y con buena luz.")

    elif menu == "📦 Stock Completo":
        st.dataframe(df)

    elif menu == "💰 Registrar Venta":
        st.link_button("🚀 IR AL FORMULARIO", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

except Exception as e:
    st.error(f"Hubo un problema: {e}")
