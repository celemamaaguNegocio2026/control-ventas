import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Celeste", page_icon="🛍️")

st.title("🚀 Escáner de Negocio")

# Carga de datos rápida
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

@st.cache_data(ttl=1) # Casi sin caché para que no se trabe
def cargar_datos():
    try:
        data = pd.read_csv(csv_url, dtype=str)
        data.columns = data.columns.str.strip()
        return data
    except:
        return None

df = cargar_datos()

if df is not None:
    # EL COMPONENTE MÁS SIMPLE POSIBLE
    st.write("### 📷 Apuntá al código de barras")
    
    # Este bloque solo hace UNA cosa: detectar y mandar el dato
    codigo_detectado = components.html(
        """
        <div id="reader" style="width: 100%;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
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

    # Si hay algo detectado (y no es el error largo anterior)
    if codigo_detectado and len(str(codigo_detectado)) < 40:
        st.divider()
        val = str(codigo_detectado).strip()
        
        # Buscamos en la primera columna (donde están tus códigos)
        col_busqueda = df.columns[0] 
        producto = df[df[col_busqueda] == val]
        
        if not producto.empty:
            st.balloons()
            for index, row in producto.iterrows():
                st.success(f"✅ ¡Detectado!: {val}")
                st.header(f"📦 {row.get('Producto', 'Sin nombre')}")
                st.metric("PRECIO", f"${row.get('Precio', '0')}")
                st.metric("STOCK", f"{row.get('Stock', '0')} un.")
        else:
            st.warning(f"Código {val} no encontrado en el Excel.")

    st.divider()
    # Buscador manual que NUNCA falla por si la cámara sigue terca
    manual = st.text_input("🔍 ¿No funciona la cámara? Escribí el nombre:")
    if manual:
        res = df[df['Producto'].str.contains(manual, case=False, na=False)]
        if not res.empty:
            st.write("Resultados encontrados:")
            st.table(res[['Producto', 'Precio', 'Stock']])

st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
