import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️")

st.title("🚀 Súper Escáner Celeste")

# Dirección de tu planilla corregida
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

@st.cache_data(ttl=60) # Se actualiza cada minuto para ver cambios en el Excel
def cargar_datos():
    try:
        data = pd.read_csv(csv_url, dtype=str)
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        st.error(f"No pude entrar al Excel. Revisá que esté compartido como 'Cualquier persona con el enlace'. Error: {e}")
        return None

df = cargar_datos()

if df is not None:
    st.markdown("### 📷 Apuntá al código de barras")
    
    # NUESTRA CREACIÓN: El motor de escaneo
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
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: decodedText}, '*');
            };
            html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
                .catch((err) => { document.getElementById('result').innerText = "❌ Error: Activa la cámara."; });
        </script>
        """,
        height=450,
    )

    if codigo_capturado:
        st.divider()
        codigo_limpio = str(codigo_capturado).strip()
        
        # Flexibilidad total para encontrar la columna de códigos
        col_codigo = "Código de Barras" if "Código de Barras" in df.columns else df.columns[0]
        producto = df[df[col_codigo] == codigo_limpio]
        
        if not producto.empty:
            st.balloons()
            for index, row in producto.iterrows():
                st.success(f"**PRODUCTO ENCONTRADO**")
                st.header(f"📦 {row.get('Producto', 'Sin nombre')}")
                c1, c2 = st.columns(2)
                c1.metric("PRECIO", f"${row.get('Precio', '0')}")
                c2.metric("STOCK", f"{row.get('Stock', '0')} un.")
        else:
            st.warning(f"El código {codigo_limpio} no está en tu Excel.")

st.divider()
st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
