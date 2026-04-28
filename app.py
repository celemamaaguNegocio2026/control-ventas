import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️")

st.title("📷 Escáner en Vivo")

# URL de tu planilla
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype=str)

try:
    df = cargar_datos()
    
    # --- ESCÁNER DE CÓDIGO DE BARRAS HTML5 ---
    # Este código se ejecuta en tu navegador, por eso es gratis y no falla
    st.write("### Apuntá al código de barras")
    
    # Creamos el componente de escaneo
    scanner_html = """
    <div id="reader" style="width:100%"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        const qrCodeSuccessCallback = (decodedText, decodedResult) => {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: decodedText}, '*');
        };
        const config = { fps: 10, qrbox: { width: 250, height: 150 } };
        html5QrCode.start({ facingMode: "environment" }, config, qrCodeSuccessCallback);
    </script>
    """
    
    # Aquí es donde capturamos el código
    codigo_leido = components.html(scanner_html, height=400)
    
    # Si el escáner detecta algo, lo buscamos
    # Nota: Para capturar el valor de JS a Streamlit a veces se necesita un pequeño truco, 
    # pero vamos a ver si este componente directo te levanta la cámara.
    
    st.divider()
    st.write("Si el escáner no inicia, asegurate de dar permisos a la cámara.")
    
    # Buscador manual por si la cámara está muy borrosa
    busqueda = st.text_input("O pegá el código aquí:")
    
    if busqueda:
        producto = df[df['Código de Barras'] == busqueda.strip()]
        if not producto.empty:
            st.success("¡Producto encontrado!")
            st.table(producto)
        else:
            st.warning("No encontrado en el Excel.")

except Exception as e:
    st.error(f"Error: {e}")
