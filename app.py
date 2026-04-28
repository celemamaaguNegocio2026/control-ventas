import streamlit as st
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Sistema de Ventas - Familia", layout="centered")

st.title("🚀 Gestión Familiar")

# URL de tu planilla (Método Directo)
url = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

# Función para leer datos
def cargar_datos():
    return pd.read_csv(csv_url)

try:
    df = cargar_datos()
    
    # Menú lateral
    menu = st.sidebar.radio("Menú de Navegación", ["🏠 Inicio", "📦 Ver Stock", "💰 Registrar Venta"])

    if menu == "🏠 Inicio":
        st.subheader(f"¡Hola Celeste!")
        st.info("La App está conectada y lista para trabajar.")
        st.write("Seleccioná una opción en el menú de la izquierda para empezar.")

    elif menu == "📦 Ver Stock":
        st.subheader("📦 Inventario en tiempo real")
        st.dataframe(df, use_container_width=True)

    elif menu == "💰 Registrar Venta":
        st.subheader("💸 Nueva Venta")
        with st.form("formulario_venta"):
            vendedora = st.selectbox("¿Quién vende?", ["Celeste", "Agustina", "Mamá"])
            producto = st.selectbox("Producto", df['Producto'].tolist() if 'Producto' in df.columns else ["Escribí el nombre abajo"])
            if 'Producto' not in df.columns:
                producto = st.text_input("Nombre del producto")
            
            cantidad = st.number_input("Cantidad", min_value=1, step=1)
            pago = st.selectbox("Método de pago", ["Efectivo", "Ualá", "Brubank", "Yoy", "Otro"])
            
            boton = st.form_submit_button("Confirmar Venta")
            
            if boton:
                st.success(f"¡Venta de {producto} registrada!")
                st.balloons()
                st.info("Nota: Por ahora la venta se visualiza aquí. En el próximo paso haremos que se guarde sola en el Excel.")

except Exception as e:
    st.error("Error al cargar los datos. Revisá que la planilla sea pública.")
