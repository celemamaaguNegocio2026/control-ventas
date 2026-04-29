import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Celeste", page_icon="🛍️")

st.title("🛡️ Gestión Familiar - Celeste")

# 1. Carga de Excel
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

@st.cache_data(ttl=2)
def cargar_datos():
    try:
        data = pd.read_csv(csv_url, dtype=str)
        data.columns = data.columns.str.strip()
        return data
    except:
        return None

df = cargar_datos()

if df is not None:
    # 2. ESCÁNER ULTRA-LIVIANO
    # Quitamos colores y bordes raros para que el celular no sufra
    val_scan = components.html(
        """
        <script src="https://unpkg.com/html5-qrcode"></script>
        <div id="reader" style="width: 100%;"></div>
        <script>
            function onScanSuccess(decodedText) {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: decodedText
                }, '*');
            }
            const html5QrCode = new Html5Qrcode("reader");
            html5QrCode.start({ facingMode: "environment" }, { fps: 10, qrbox: 250 }, onScanSuccess);
        </script>
        """,
        height=350,
    )

    # 3. BUSCADOR
    if val_scan and len(str(val_scan)) < 30:
        st.divider()
        codigo = str(val_scan).strip()
        
        # Buscamos en tu columna: "Codigo de barra"
        col_busqueda = "Codigo de barra"
        producto = df[df[col_busqueda] == codigo]
        
        if not producto.empty:
            st.balloons()
            for index, row in producto.iterrows():
                st.success(f"✅ DETECTADO: {codigo}")
                st.header(f"📦 {row['Producto']}")
                st.metric("PRECIO", f"${row['Precio']}")
                st.metric("STOCK", f"{row['Stock']} un.")
        else:
            st.warning(f"El código {codigo} no está en tu Excel.")

    st.divider()
    manual = st.text_input("🔍 O buscá por nombre:")
    if manual:
        res = df[df['Producto'].str.contains(manual, case=False, na=False)]
        if not res.empty:
            st.table(res[['Producto', 'Precio', 'Stock']])

st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
