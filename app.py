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
    st.write("### 📷 Apuntá al código")
    st.info("💡 Tip: Si el código está vertical como en la foto, girá un poco el celular o la botella.")
    
    # ESCÁNER REFORZADO PARA CÓDIGOS VERTICALES
    codigo_leido = components.html(
        """
        <div id="reader" style="width: 100%; border-radius: 10px;"></div>
        <script src="https://unpkg.com/html5-qrcode"></script>
        <script>
            const html5QrCode = new Html5Qrcode("reader");
            const config = { 
                fps: 25, 
                qrbox: { width: 300, height: 200 },
                aspectRatio: 1.0
            };
            
            function onScanSuccess(decodedText) {
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: decodedText
                }, '*');
            }

            // Intentamos con una configuración de mayor sensibilidad
            html5QrCode.start(
                { facingMode: "environment" }, 
                config, 
                onScanSuccess
            );
        </script>
        """,
        height=400,
    )

    if codigo_leido and "DeltaGenerator" not in str(codigo_leido):
        st.divider()
        val = str(codigo_leido).strip()
        
        # Buscamos en tu columna 'Codigo de barra'
        col_busqueda = "Codigo de barra"
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
            st.write("Verificá que el número en el Excel sea exactamente el mismo.")

    st.divider()
    # Buscador manual siempre visible por si el reflejo de la botella molesta
    manual = st.text_input("🔍 O buscá por nombre/número manualmente:")
    if manual:
        res = df[df.apply(lambda row: manual.lower() in row.astype(str).str.lower().values, axis=1)]
        if not res.empty:
            st.table(res)

st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
