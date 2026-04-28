import streamlit as st
import pandas as pd

# Configuración visual de la App
st.set_page_config(page_title="Sistema Gestión Familiar", page_icon="🛍️")

st.title("🛍️ Gestión Familiar - Celeste")

# Conexión con tu planilla (Método Directo)
url_planilla = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"
csv_url = url_planilla.replace("/edit?usp=sharing", "/export?format=csv&gid=0")

# Link definitivo de tu Formulario de Google
url_formulario = "https://docs.google.com/forms/d/e/1FAIpQLSeAkoHMMcoBV516gZcOSgzheOUfXHv9q2Fy_vpWKBFEIUzKWw/viewform?usp=sf_link"

def cargar_datos():
    return pd.read_csv(csv_url)

try:
    df = cargar_datos()
    
    # Menú lateral para navegar
    menu = st.sidebar.radio("MENÚ PRINCIPAL", ["🏠 Inicio", "📦 Ver Stock / Precios", "💰 Registrar Venta"])

    if menu == "🏠 Inicio":
        st.subheader("¡Bienvenida!")
        st.write("Esta es la App oficial para el negocio familiar.")
        st.info("Usá el menú de la izquierda para ver qué hay en stock o para cargar una venta nueva.")
        st.write("---")
        st.write("💡 *Consejo: Podés usar esta App desde tu celular entrando al mismo link.*")

    elif menu == "📦 Ver Stock / Precios":
        st.subheader("📦 Inventario en tiempo real")
        st.write("Esto es lo que hay cargado en el Excel actualmente:")
        st.dataframe(df, use_container_width=True)
        if st.button("🔄 Actualizar Datos"):
            st.rerun()

    elif menu == "💰 Registrar Venta":
        st.subheader("💸 Cargar Nueva Venta")
        st.write("Hacé clic en el botón de abajo para abrir el formulario y registrar la operación.")
        
        # Botón grande y llamativo
        st.link_button("🚀 ABRIR FORMULARIO DE VENTA", url_formulario, use_container_width=True)
        
        st.write("---")
        st.caption("Una vez que envíes el formulario, la venta aparecerá automáticamente en la pestaña 'Respuestas' de tu planilla de Google.")

except Exception as e:
    st.error("Hubo un problema al conectar con la planilla. Revisá que siga siendo pública.")
