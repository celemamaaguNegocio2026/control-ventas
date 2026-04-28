import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️", layout="centered")

st.title("🚀 Súper Escáner Celeste")

# 1. Cargar tus datos del Excel
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

@st.cache_data
def cargar_datos():
    return pd.read_csv(csv_url, dtype=str)

df = cargar_datos()

# 2. EL ESCÁNER (Creado a medida por nosotras)
# Este bloque de abajo es el que "fabrica" el escáner que funciona en Android
st.markdown("### 📷 Apuntá al código de barras")

codigo_capturado = components.html(
    """
    <div id="reader" style="width: 100%; border-radius: 15px; overflow: hidden;"></div>
    <div id="result" style="text-align: center; font-weight: bold; font-size: 20px; color: #008000; margin-top: 10px;">Buscando código...</div>
    
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        const config = { fps: 15, qrbox: { width: 280, height: 180 } };
        
        const onScanSuccess = (decodedText) => {
            document.getElementById('result').innerText = "✅ ¡Detectado!: " + decodedText;
            // Enviamos el código a Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: decodedText
            }, '*');
        };

        // Iniciamos la cámara trasera automáticamente
        html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
            .catch((err) => {
                document.getElementById('result').innerText = "❌ Error: Activa la cámara en los permisos.";
            });
    </script>
    """,
    height=450,
)

# 3. MOSTRAR EL RESULTADO
# El valor que "escupe" el código de arriba llega aquí:
if codigo_capturado:
    st.divider()
    codigo_limpio = str(codigo_capturado).strip()
    
    # Buscamos en el Excel
    producto = df[df['Código de Barras'] == codigo_limpio]
    
    if not producto.empty:
        st.balloons()
        for index, row in producto.iterrows():
            st.success(f"**PRODUCTO ENCONTRADO**")
            st.header(f"📦 {row['Producto']}")
            c1, c2 = st.columns(2)
            c1.metric("PRECIO", f"${row['Precio']}")
            c2.metric("STOCK", f"{row['Stock']} un.")
    else:
        st.warning(f"El código {codigo_limpio} no está en tu Excel.")

st.divider()
st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
