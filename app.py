import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️", layout="centered")

st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)
st.title("🛡️ Sistema Celeste v1.0")

# --- 1. CONEXIÓN AL EXCEL ---
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
    # --- 2. NUESTRO ESCÁNER PROPIO (VISIÓN ARTIFICIAL) ---
    st.write("### 📷 Lector de Barras")
    
    # Creamos el componente de visión que se comunica con el Excel
    # Este código corre 100% en tu celular para que sea veloz
    codigo_detectado = components.html(
        """
        <div id="scanner-container" style="width: 100%; border-radius: 20px; overflow: hidden; border: 4px solid #4CAF50;">
            <div id="interactive" class="viewport"></div>
        </div>
        <div id="resultado-lectura" style="text-align: center; font-size: 20px; font-weight: bold; padding: 10px; color: #2e7d32;">
            Apuntá al código de barras
        </div>

        <script src="https://cdn.jsdelivr.net/npm/@ericblade/quagga2/dist/quagga.min.js"></script>
        <script>
            Quagga.init({
                inputStream: {
                    name: "Live",
                    type: "LiveStream",
                    target: document.querySelector('#interactive'),
                    constraints: { facingMode: "environment" }
                },
                decoder: {
                    readers: ["ean_reader", "ean_8_reader", "code_128_reader", "upc_reader"]
                },
                locate: true
            }, function(err) {
                if (err) { console.log(err); return }
                Quagga.start();
            });

            Quagga.onDetected(function(result) {
                var code = result.codeResult.code;
                document.getElementById('resultado-lectura').innerText = "✅ DETECTADO: " + code;
                
                // Le avisamos a nuestra App de Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: code
                }, '*');
            });
        </script>
        <style>
            #interactive video { width: 100%; height: auto; }
            canvas.drawingBuffer { display: none; }
        </style>
        """,
        height=450,
    )

    # --- 3. RESPUESTA AUTOMÁTICA DEL PROGRAMA ---
    if codigo_detectado:
        st.divider()
        val = str(codigo_detectado).strip()
        
        # Buscamos en tu columna: "Codigo de barra"
        col_busqueda = "Codigo de barra"
        producto = df[df[col_busqueda] == val]
        
        if not producto.empty:
            st.balloons()
            for index, row in producto.iterrows():
                st.success(f"📦 PRODUCTO ENCONTRADO")
                st.header(row['Producto'])
                st.metric("PRECIO", f"${row['Precio']}")
                st.metric("STOCK", f"{row['Stock']} un.")
        else:
            st.warning(f"El código {val} no figura en el Excel.")

st.divider()
st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
