import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestión Celeste", page_icon="🛍️", layout="centered")

# Estilo para celulares: botones grandes y texto claro
st.markdown("""
    <style>
    .stTextInput > div > div > input { font-size: 22px !important; }
    button { height: 3em !important; width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛍️ Sistema de Ventas")

url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype={'Código de Barras': str})

try:
    df = cargar_datos()
    
    st.write("### 🔍 Buscador Inteligente")
    busqueda = st.text_input("Pegá el código o escribí el nombre:", key="buscador")
    
    if busqueda:
        # Buscamos coincidencias
        resultado = df[
            (df['Código de Barras'] == busqueda) | 
            (df['Producto'].str.contains(busqueda, case=False, na=False))
        ]
        
        if not resultado.empty:
            for index, row in resultado.iterrows():
                with st.container():
                    st.success(f"**{row['Producto']}**")
                    c1, c2 = st.columns(2)
                    c1.metric("Precio", f"${row['Precio']}")
                    c2.metric("Stock", f"{row['Stock']} un.")
                    st.divider()
        else:
            st.warning("No se encontró el producto. Verificá el código.")

    st.divider()
    
    # Botonera principal
    st.link_button("💰 REGISTRAR VENTA (Formulario)", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")
    
    if st.button("📋 Ver Inventario Completo"):
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
