import streamlit as st
import pandas as pd
import cv2
import numpy as np

st.set_page_config(page_title="Gestión Familiar - Celeste", page_icon="🛍️")

st.title("📷 Escáner Celeste")

# Configuración de tu planilla
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype={'Código de Barras': str})

try:
    df = cargar_datos()
    
    st.write("### Escaneá tu producto aquí")
    
    # Este componente usa la cámara nativa del celular (la que mejor enfoca)
    foto = st.camera_input("Apuntá al código de barras y sacá la foto")
    
    if foto:
        # Convertir la imagen para que el sistema la lea
        file_bytes = np.asarray(bytearray(foto.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        
        # Detector de códigos
        detector = cv2.barcode.BarcodeDetector()
        ok, info, tipo, puntos = detector.detectAndDecode(img)
        
        if ok and info[0]:
            codigo = str(info[0])
            st.success(f"✅ ¡Leído con éxito! Código: {codigo}")
            
            # Buscar en el Excel
            resultado = df[df['Código de Barras'] == codigo]
            
            if not resultado.empty:
                st.balloons()
                st.table(resultado)
            else:
                st.warning(f"El código {codigo} no está en tu lista de Excel.")
        else:
            st.error("❌ No se pudo leer el código. Intentá sacarla un poquito más lejos para que el celu pueda enfocar bien las barritas.")

    st.divider()
    
    # Botón para ir al formulario si querés vender
    st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

except Exception as e:
    st.error(f"Error: {e}")
