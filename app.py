import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Celeste", page_icon="🛍️")

st.title("🚀 Escáner de Negocio")

# Carga de datos
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

@st.cache_data(ttl=5)
def cargar_datos():
    try:
        data = pd.read_csv(csv_url, dtype=str)
        data.columns = data.columns.str.strip()
        return data
    except:
        return None

df = cargar_datos()

if df is not None:
    # 1. El Escáner (HTML/JS)
    # Este bloque detecta el código y lo "grita" para que Streamlit lo escuche
    st.write("### 📷 Apuntá al código")
    
    codigo_leido = components.html(
        """
        <div id="reader" style="width: 100%;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            function onScanSuccess(decodedText) {
                // Enviamos el dato directamente
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: decodedText
                }, '*');
            }
            const html5QrCode = new Html5Qrcode("reader");
            html5QrCode.start({ facingMode: "environment" }, { fps: 15, qrbox: 250 }, onScanSuccess);
        </script>
        """,
        height=350,
    )

    # 2. El Buscador (Lógica de Python)
    # Aquí es donde ocurre la magia: buscamos lo que detectó el componente
    if codigo_leido:
        # Convertimos a string y limpiamos cualquier residuo de código técnico
        codigo_final = str(codigo_leido).strip()
        
        # Filtramos para que no busque el texto largo de error si aparece
        if len(codigo_final) < 50: 
            st.divider()
            
            # Buscamos la columna de códigos (flexible)
            col_cod = next((c for c in df.columns if "barra" in c.lower() or "codigo" in c.lower()), df.columns[0])
            producto = df[df[col_cod] == codigo_final]
            
            if not producto.empty:
                st.balloons()
                for index, row in producto.iterrows():
                    st.success(f"✅ ¡Detectado!: {codigo_final}")
                    st.header(f"📦 {row.get('Producto', 'Sin nombre')}")
                    c1, c2 = st.columns(2)
                    c1.metric("PRECIO", f"${row.get('Precio', '0')}")
                    c2.metric("STOCK", f"{row.get('Stock', '0')} un.")
            else:
                st.warning(f"El código {codigo_final} no está en tu Excel.")

    st.divider()
    # Buscador manual por si la luz es mala
    manual = st.text_input("🔍 O buscá por nombre:")
    if manual:
        res = df[df['Producto'].str.contains(manual, case=False, na=False)]
        if not res.empty:
            st.dataframe(res, hide_index=True)

st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
