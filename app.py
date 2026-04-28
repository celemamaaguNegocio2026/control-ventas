import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Gestión Familiar - Celeste", page_icon="🛍️")

st.title("🛍️ Gestión Familiar - Celeste")

# URL de tu planilla (Asegurate que sea esta la correcta)
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

# Función para cargar datos del Excel
def cargar_datos():
    return pd.read_csv(csv_url, dtype={'Código de Barras': str})

try:
    df = cargar_datos()
    
    # Menú de navegación
    menu = st.sidebar.radio("MENÚ", ["🏠 Inicio", "🔍 Buscar Producto", "📦 Stock Completo", "💰 Registrar Venta"])

    if menu == "🏠 Inicio":
        st.subheader("¡Bienvenida!")
        st.write("El sistema se ha reiniciado para eliminar errores de cámara.")
        st.info("Usá el menú de la izquierda para empezar.")

    elif menu == "🔍 Buscar Producto":
        st.subheader("🔎 Buscador de Inventario")
        busqueda = st.text_input("Escribí el nombre del producto o el código de barras:")
        
        if busqueda:
            # Busca en la columna 'Producto' o 'Código de Barras'
            resultado = df[
                df['Producto'].str.contains(busqueda, case=False, na=False) | 
                df['Código de Barras'].str.contains(busqueda, na=False)
            ]
            
            if not resultado.empty:
                st.success("¡Producto encontrado!")
                st.table(resultado)
            else:
                st.warning("No se encontró ningún producto con ese nombre o código.")

    elif menu == "📦 Stock Completo":
        st.subheader("📋 Lista Completa de Productos")
        st.dataframe(df, use_container_width=True)

    elif menu == "💰 Registrar Venta":
        st.subheader("💸 Cargar Nueva Venta")
        st.write("Hacé clic abajo para abrir el formulario de ventas:")
        st.link_button("🚀 ABRIR FORMULARIO", "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform")

except Exception as e:
    st.error(f"Error al conectar con la planilla: {e}")
