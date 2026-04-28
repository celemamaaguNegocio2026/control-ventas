import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️", layout="centered")

st.title("🛡️ Gestión Familiar - Celeste")

# --- 1. CONEXIÓN AL EXCEL ---
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

@st.cache_data(ttl=5)
def cargar_datos():
    try:
        data = pd.read_csv(csv_url, dtype=str)
        data.columns = data.columns.str.strip()
        return data
    except Exception as e:
        return None

df = cargar_datos()

if df is not None:
    st.markdown("### 📷 ESCÁNER AUTOMÁTICO")
    
    # --- 2. EL ESCÁNER CREADO A MEDIDA ---
    # Este bloque es nuestro "invento": un escáner que no falla en Android
    val_scan = components.html(
        """
        <div id="reader" style="width: 100%; border: 3px solid #2ecc71; border-radius: 15px;"></div>
        <div id="status" style="text-align:center; margin-top:10px; font-weight:bold; color:#27ae60;">
            Buscando código...
        </div>
        
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            const html5QrCode = new Html5Qrcode("reader");
            
            // Configuración de ultra-sensibilidad para botellas y códigos verticales
            const config = { 
                fps: 30, 
                qrbox: { width: 300, height: 200 },
                experimentalFeatures: { useBarCodeDetectorIfSupported: true }
            };
            
            function onScanSuccess(decodedText) {
                document.getElementById('status').innerHTML = "✅ ¡DETECTADO!";
                // El "Grito": Mandamos el dato al padre (Streamlit)
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: decodedText
                }, '*');
            }

            // Iniciamos la cámara con prioridad en la trasera (environment)
            html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess)
                .catch(err => {
                    document.getElementById('status').innerHTML = "❌ Error: Activa los permisos de cámara";
                    document.getElementById('status').style.color = "red";
                });
        </script>
        """,
        height=450,
    )

    # --- 3. EL BUSCADOR LÓGICO ---
    # Solo entramos aquí si el escáner capturó algo real
    if val_scan and isinstance(val_scan, str) and len(val_scan) < 40:
        st.divider()
        codigo_limpio = val_scan.strip()
        
        # Buscamos en la columna de tu Excel
        col_busqueda = "Codigo de barra"
        producto = df[df[col_busqueda] == codigo_limpio]
        
        if not producto.empty:
            st.balloons()
            for index, row in producto.iterrows():
                st.success(f"📦 PRODUCTO ENCONTRADO")
                st.header(row['Producto'])
                c1, c2 = st.columns(2)
                c1.metric("PRECIO ACTUAL", f"${row['Precio']}")
                c2.metric("STOCK EN TIENDA", f"{row['Stock']} un.")
        else:
            st.warning(f"El código {codigo_limpio} no está en tu Excel.")

    st.divider()
    # Buscador manual que no depende de la cámara (por seguridad)
    manual = st.text_input("🔍 O buscá escribiendo:")
    if manual:
        res = df[df['Producto'].str.contains(manual, case=False, na=False)]
        if not res.empty:
            st.dataframe(res[['Producto', 'Precio', 'Stock']], hide_index=True)

st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

    
