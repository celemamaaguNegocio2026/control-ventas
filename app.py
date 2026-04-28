import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Celeste", page_icon="🛍️")

st.title("🚀 Escáner de Negocio")

# Carga de datos
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

@st.cache_data(ttl=1)
def cargar_datos():
    try:
        data = pd.read_csv(csv_url, dtype=str)
        data.columns = data.columns.str.strip()
        return data
    except:
        return None

df = cargar_datos()

if df is not None:
    st.write("### 📷 Apuntá al código de barras")
    
    # El componente que sí lograba detectar números
    codigo_leido = components.html(
        """
        <div id="reader" style="width: 100%;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            const html5QrCode = new Html5Qrcode("reader");
            function onScanSuccess(decodedText) {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: decodedText
                }, '*');
            }
            html5QrCode.start({ facingMode: "environment" }, { fps: 20, qrbox: 280 }, onScanSuccess);
        </script>
        """,
        height=400,
    )

    # Si hay una detección (Cualquier cosa que mande el componente)
    if codigo_leido:
        # Convertimos a texto y limpiamos
        val = str(codigo_leido).strip()
        
        # Si el valor parece un código real (no el texto de error de Streamlit)
        if "DeltaGenerator" not in val:
            st.divider()
            # Buscamos en la columna 'Codigo de barra' (tal cual está en tu Excel)
            col_busqueda = "Codigo de barra"
            
            # Buscamos coincidencia exacta
            producto = df[df[col_busqueda] == val]
            
            if not producto.empty:
                st.balloons()
                for index, row in producto.iterrows():
                    st.success(f"✅ ¡Detectado!: {val}")
                    st.header(f"📦 {row['Producto']}")
                    c1, c2 = st.columns(2)
                    c1.metric("PRECIO", f"${row['Precio']}")
                    c2.metric("STOCK", f"{row['Stock']} un.")
            else:
                st.warning(f"El código {val} no está en tu Excel.")
        else:
            # Si todavía no hay una lectura real, no mostramos error, solo esperamos
            st.info("Esperando lectura clara...")

    st.divider()
    # Buscador manual de respaldo
    manual = st.text_input("🔍 O buscá por nombre:")
    if manual:
        res = df[df['Producto'].str.contains(manual, case=False, na=False)]
        if not res.empty:
            st.table(res[['Producto', 'Precio', 'Stock']])

st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
