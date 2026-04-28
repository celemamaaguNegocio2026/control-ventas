import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestión Familiar - Celeste", page_icon="🛍️")

st.title("🛍️ Sistema Celeste")

# Conexión a tu planilla
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

def cargar_datos():
    return pd.read_csv(csv_url, dtype={'Código de Barras': str})

try:
    df = cargar_datos()
    
    menu = st.sidebar.radio("MENÚ", ["🏠 Inicio", "🔍 Buscar Producto", "📦 Stock Completo", "💰 Registrar Venta"])

    if menu == "🔍 Buscar Producto":
        st.subheader("🔎 Buscador Rápido")
        # Aquí podés escribir el nombre o el código
        busqueda = st.text_input("Escribí el nombre del producto o el código de barras:")
        
        if busqueda:
            # Filtra por nombre o por código automáticamente
            resultado = df[
                df['Producto'].str.contains(busqueda, case=False, na=False) | 
                df['Código de Barras'].str.contains(busqueda, na=False)
            ]
            
            if not resultado.empty:
                st.success("¡Producto encontrado!")
                st.table(resultado)
            else:
                st.warning("No se encontró nada con ese dato. ¿Está bien escrito?")

    elif menu == "🏠 Inicio":
        st.info("Bienvenida. El sistema se ha reiniciado para corregir los errores visuales.")
        st.write("Usá el menú de la izquierda para navegar.")

    elif menu == "📦 Stock Completo":
        st.subheader("📋 Inventario en el Excel")
        st.dataframe(df, use_container_width=True)

    elif menu == "💰 Registrar Venta":
        st.subheader("💸 Cargar Venta")
        st.link_button("🚀 ABRIR FORMULARIO", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

except Exception as e:
    st.error(f"Error de conexión: {e}")
