import streamlit as st
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️")

# --- MOTOR DE CÁMARA JAVASCRIPT ---
st.markdown("""
    <script src="https://unpkg.com/html5-qrcode"></script>
    <div id="reader" style="width: 100%;"></div>
    <script>
        function onScanSuccess(decodedText, decodedResult) {
            // Enviamos el código detectado a Streamlit
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: decodedText}, '*');
        }
        let html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 });
        html5QrcodeScanner.render(onScanSuccess);
    </script>
""", unsafe_allow_html=True)

# --- LÓGICA DE LA APP ---
st.title("📷 Escáner en Vivo")

url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype=str)

try:
    df = cargar_datos()
    
    # Capturamos el código que viene del escáner arriba
    codigo_detectado = st.text_input("Código detectado actualmente:", key="input_scan")

    if codigo_detectado:
        # Limpiamos el código por si trae espacios
        codigo_limpio = codigo_detectado.strip()
        
        # Buscamos en el Excel
        producto = df[df['Código de Barras'] == codigo_limpio]
        
        if not producto.empty:
            st.balloons()
            for index, row in producto.iterrows():
                st.success(f"📦 PRODUCTO: {row['Producto']}")
                st.metric("Precio", f"${row['Precio']}")
                st.metric("Stock actual", f"{row['Stock']} unidades")
        else:
            st.warning(f"El código {codigo_limpio} no está en tu lista.")

    st.divider()
    st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

except Exception as e:
    st.error(f"Error de conexión: {e}")
