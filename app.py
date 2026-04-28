import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Celeste", page_icon="🛍️")

# Estilo para que se vea bien en el celu
st.markdown("<style>iframe {border-radius: 10px; border: 1px solid #ddd;}</style>", unsafe_allow_html=True)

st.title("🚀 Escáner de Negocio")

# Dirección de tu planilla (Verificada)
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
    st.write("### 📷 Apuntá al código de barras")
    
    # NUEVO ESCÁNER REFORZADO
    # Usamos una variable de estado (session_state) para que el dato no se pierda ni se ensucie
    codigo_input = components.html(
        """
        <div id="reader" style="width: 100%;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            const html5QrCode = new Html5Qrcode("reader");
            const onScanSuccess = (decodedText) => {
                // Solo enviamos el texto plano
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: decodedText
                }, '*');
            };
            const config = { fps: 15, qrbox: { width: 250, height: 150 } };
            html5QrCode.start({ facingMode: "environment" }, config, onScanSuccess);
        </script>
        """,
        height=350,
    )

    # Solo buscamos si el código es un texto real y no el objeto DeltaGenerator
    if codigo_input and isinstance(codigo_input, str):
        st.divider()
        codigo_limpio = codigo_input.strip()
        
        # Buscador de columna flexible
        col_busqueda = next((c for c in df.columns if "barra" in c.lower() or "codigo" in c.lower()), df.columns[0])

        producto = df[df[col_busqueda] == codigo_limpio]
        
        if not producto.empty:
            st.balloons()
            for index, row in producto.iterrows():
                st.success(f"✅ ¡Detectado!: {codigo_limpio}")
                st.header(f"📦 {row.get('Producto', 'Sin nombre')}")
                c1, c2 = st.columns(2)
                c1.metric("PRECIO", f"${row.get('Precio', '0')}")
                c2.metric("STOCK", f"{row.get('Stock', '0')} un.")
        else:
            st.warning(f"El código {codigo_limpio} no está en tu Excel.")
    
    # Por si el escáner falla, siempre dejamos el buscador manual abajo
    st.divider()
    manual = st.text_input("O escribí el nombre/código manualmente:")
    if manual:
        res = df[df.apply(lambda row: manual.lower() in row.astype(str).str.lower().values, axis=1)]
        if not res.empty:
            st.table(res)

st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
