import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️", layout="centered")

st.title("🛡️ Sistema de Ventas Celeste")

# 1. CARGA DE EXCEL (Conexión directa)
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

@st.cache_data(ttl=5)
def cargar_datos():
    try:
        data = pd.read_csv(csv_url, dtype=str)
        data.columns = data.columns.str.strip() # Limpia espacios en nombres de columnas
        return data
    except Exception as e:
        st.error(f"Error de conexión con Excel: {e}")
        return None

df = cargar_datos()

if df is not None:
    st.markdown("### 📷 ESCÁNER EN VIVO")
    st.caption("Apuntá al código de barras. Si es vertical, girá el celular.")

    # 2. EL MOTOR DE ESCANEO (JavaScript Puro)
    # Este bloque es el que "atrapa" el número y lo manda a la lista
    val_scan = components.html(
        """
        <div id="reader" style="width: 100%; border: 2px solid #4CAF50; border-radius: 10px;"></div>
        <div id="msg" style="text-align:center; padding:10px; font-family:sans-serif; color:#666;">Esperando cámara...</div>
        
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            const html5QrCode = new Html5Qrcode("reader");
            const config = { fps: 20, qrbox: { width: 280, height: 180 } };
            
            function onScanSuccess(decodedText) {
                document.getElementById('msg').innerHTML = "✅ ¡CÓDIGO DETECTADO!";
                // Mandamos el número a Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: decodedText
                }, '*');
            }

            html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
                .then(() => { document.getElementById('msg').innerHTML = "🎥 Cámara activa - Buscando barras..."; })
                .catch(err => { document.getElementById('msg').innerHTML = "❌ Error de cámara: " + err; });
        </script>
        """,
        height=420,
    )

    # 3. LÓGICA DE BÚSQUEDA
    # Si detectamos un código y no es el mensaje de error de Streamlit
    if val_scan and len(str(val_scan)) < 30: 
        st.divider()
        codigo = str(val_scan).strip()
        
        # Buscamos en la columna que coincida con tu Excel (Codigo de barra)
        # Hacemos que la búsqueda sea inteligente
        col_busqueda = next((c for c in df.columns if "barra" in c.lower() or "codigo" in c.lower()), df.columns[0])
        
        producto = df[df[col_busqueda] == codigo]
        
        if not producto.empty:
            st.balloons()
            for index, row in producto.iterrows():
                st.success(f"📦 ¡ENCONTRADO!")
                st.header(row.get('Producto', 'Producto sin nombre'))
                c1, c2 = st.columns(2)
                c1.metric("PRECIO", f"${row.get('Precio', '0')}")
                c2.metric("STOCK", f"{row.get('Stock', '0')} un.")
        else:
            st.warning(f"El código {codigo} no figura en tu Excel. ¡Revisalo!")

    st.divider()
    # Buscador manual de emergencia
    manual = st.text_input("🔍 O buscá escribiendo el nombre:")
    if manual:
        res = df[df['Producto'].str.contains(manual, case=False, na=False)]
        if not res.empty:
            st.dataframe(res[['Producto', 'Precio', 'Stock']], hide_index=True)

st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
