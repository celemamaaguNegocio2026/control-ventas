import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config(page_title="Sistema Pro Celeste", page_icon="🛍️")

st.title("🛡️ Sistema Celeste v1.1")

# --- 1. CONEXIÓN AL EXCEL ---
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

@st.cache_data(ttl=5)
def cargar_datos():
    try:
        data = pd.read_csv(csv_url, dtype=str)
        # Limpiamos los nombres de las columnas por si tienen espacios invisibles
        data.columns = [str(c).strip() for c in data.columns]
        return data
    except:
        return None

df = cargar_datos()

if df is not None:
    st.write("### 📷 Lector de Barras")
    
    # NUESTRO ESCÁNER PROPIO
    codigo_detectado = components.html(
        """
        <div id="scanner-container" style="width: 100%; border-radius: 20px; overflow: hidden; border: 4px solid #4CAF50;">
            <div id="interactive" class="viewport"></div>
        </div>
        <div id="resultado-lectura" style="text-align: center; font-size: 20px; font-weight: bold; padding: 10px; color: #2e7d32; font-family: sans-serif;">
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
                window.parent.postMessage({type: 'streamlit:setComponentValue', value: code}, '*');
            });
        </script>
        <style>
            #interactive video { width: 100%; height: auto; }
            canvas.drawingBuffer { display: none; }
        </style>
        """,
        height=400,
    )

    if codigo_detectado:
        st.divider()
        val = str(codigo_detectado).strip()
        
        # --- BUSCADOR INTELIGENTE DE COLUMNA ---
        # Buscamos cuál de tus columnas es la de los códigos
        col_busqueda = None
        posibles_nombres = ["codigo", "barra", "barras", "code"]
        
        for c in df.columns:
            if any(n in c.lower() for n in posibles_nombres):
                col_busqueda = c
                break
        
        # Si no encontró ninguna con esos nombres, usa la primera columna por defecto
        if not col_busqueda:
            col_busqueda = df.columns[0]

        # Buscamos el producto
        producto = df[df[col_busqueda] == val]
        
        if not producto.empty:
            st.balloons()
            for index, row in producto.iterrows():
                st.success(f"📦 PRODUCTO ENCONTRADO")
                # Buscamos la columna del nombre del producto
                col_nombre = next((c for c in df.columns if "prod" in c.lower() or "nombre" in c.lower()), df.columns[1])
                st.header(row[col_nombre])
                
                c1, c2 = st.columns(2)
                # Buscamos precios y stock de forma flexible
                col_precio = next((c for c in df.columns if "prec" in c.lower()), "Precio")
                col_stock = next((c for c in df.columns if "stock" in c.lower()), "Stock")
                
                c1.metric("PRECIO", f"${row.get(col_precio, '0')}")
                c2.metric("STOCK", f"{row.get(col_stock, '0')} un.")
        else:
            st.warning(f"El código {val} no está en tu Excel (Columna: {col_busqueda})")

st.divider()
st.link_button("💰 REGISTRAR VENTA", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
