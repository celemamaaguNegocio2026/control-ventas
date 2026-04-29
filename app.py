import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="celeagumama - Gestión", layout="centered")

# --- ID DE TU EXCEL (Ya lo puse por vos) ---
ID_EXCEL = "1zcya1QAR3hnbddUruZSvfSkLATnM3XCvqrMndEY_UAg"

# Función para leer cualquier pestaña de tu Excel
def leer_hoja(nombre_hoja):
    url = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL}/gviz/tq?tqx=out:csv&sheet={nombre_hoja}"
    return pd.read_csv(url)

# --- PASO 1: USUARIOS Y PINs ---
usuarios_fijos = {
    "Celeste": "1997", 
    "Agu": "1995", 
    "Mamá": "1975"
}

# --- CONTROL DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario'] = None

# --- PANTALLA DE LOGIN ---
if not st.session_state['autenticado']:
    st.markdown("<h1 style='text-align: center;'>🔐 Acceso Gestión Familiar</h1>", unsafe_allow_html=True)
    
    user = st.selectbox("¿Quién sos?", ["Seleccionar...", "Celeste", "Agu", "Mamá"])
    
    if user != "Seleccionar...":
        pin = st.text_input(f"Hola {user}, ingresá tu PIN:", type="password", max_chars=4)
        
        if st.button("ENTRAR AL SISTEMA", use_container_width=True):
            if pin == usuarios_fijos.get(user):
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = user
                st.rerun()
            else:
                st.error("PIN incorrecto. Revisá el año.")

# --- PANTALLA PRINCIPAL (Solo se ve si el PIN es correcto) ---
else:
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    st.write(f"## ¡Bienvenida, {st.session_state['usuario']}!")
    st.write("---")
    
    st.success("✅ Conexión con Google Sheets configurada.")

    # BOTÓN DE PRUEBA
    if st.button("🔄 Probar Conexión con mi Excel"):
        try:
            # Intentamos leer la pestaña USUARIOS que creaste
            df_usuarios = leer_hoja("USUARIOS")
            st.write("### Datos encontrados en tu pestaña 'USUARIOS':")
            st.dataframe(df_usuarios)
            st.balloons()
        except Exception as e:
            st.error("No se pudo leer el Excel.")
            st.info("Asegurate de que en el Excel hiciste clic en 'Compartir' -> 'Cualquier persona con el enlace' -> 'Editor'.")
            st.write(f"Error técnico: {e}")

    st.write("---")
    st.write("### 🚀 Próximo Paso:")
    st.write("Si pudiste ver tus datos arriba, avisame y armamos el formulario para **Cargar los Gastos** y que la App calcule la meta sola.")
