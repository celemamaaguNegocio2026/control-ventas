import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️")

st.title("🛡️ Gestión Familiar - Celeste")

# --- 1. CONEXIÓN AL EXCEL ---
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

@st.cache_data(ttl=2) # Bajamos el tiempo para que sea instantáneo
def cargar_datos():
    try:
        data = pd.read_csv(csv_url, dtype=str)
        data.columns = data.columns.str.strip()
        return data
    except:
        return None

df = cargar_datos()

if df is not None:
    st.markdown("### 📷 ESCÁNER ACTIVO")
    
    # --- 2. EL ESCÁNER (Con auto-refresco) ---
    # Usamos una "llave" (key) para que Streamlit sepa que el dato cambió
    val_scan = components.html(
        """
        <div id="reader" style="width: 100%; border: 3px solid #2ecc71; border-radius: 15px;"></div>
        <div id="status" style="text-align:center; margin-top:10px; font-weight:bold; color:#27ae60; font-family:sans-serif;">
            Buscando código...
        </div>
        
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            const html5QrCode = new Html5Qrcode("reader");
            const config = { fps: 30, qrbox: { width: 250, height: 150 } };
            
            function onScanSuccess(decodedText) {
                document.getElementById('status').innerHTML = "✅ ¡DETECTADO!: " + decodedText;
                // Enviamos el dato y forzamos a Streamlit a reaccionar
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: decodedText
                }, '*');
            }

            html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess);
        </script>
        """,
        height=380,
    )

    # --- 3. MOSTRAR RESULTADO INMEDIATO ---
    # Si el escáner capturó algo, lo procesamos
    if val_scan:
        st.divider()
        codigo_encontrado = str(val_scan).strip()
        
        # Filtramos basura técnica
        if len(codigo_encontrado) < 30 and "DeltaGenerator" not in codigo_encontrado:
            # Buscamos en tu columna exacta
            col_busqueda = "Codigo de barra"
            producto = df[df[col_busqueda] == codigo_encontrado]
            
            if not producto.empty:
                st.balloons()
                for index, row in producto.iterrows():
                    st.success(f"📦 PRODUCTO: {row['Producto']}")
                    st.subheader(f"💰 PRECIO: ${row['Precio']}")
                    st.info(f"📊 STOCK: {row['Stock']} unidades")
            else:
                st.warning(f"Código {codigo_encontrado} no está en el Excel.")
                # Por si acaso, mostramos los primeros códigos para que verifiques
                with st.expander("Ver lista de códigos en Excel"):
                    st.write(df[[col_busqueda, 'Producto']].head())

    st.divider()
    manual = st.text_input("🔍 O escribí el nombre manualmente:")
    if manual:
        res = df[df['Producto'].str.contains(manual, case=False, na=False)]
        if not res.empty:
            st.table(res[['Producto', 'Precio', 'Stock']])

st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

    
