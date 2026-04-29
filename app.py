import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="celeagumama - Gestión", layout="centered")

# Simulación de los datos (Paso 1: Usuarios)
# Asegurate de que los PIN estén entre comillas como textos
usuarios = {
    "Celeste": "1234", 
    "Agu": "5678",
    "Mamá": "9012"
}

# --- CONTROL DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario'] = None

# --- PANTALLA DE LOGIN ---
if not st.session_state['autenticado']:
    st.markdown("<h1 style='text-align: center;'>🔐 Acceso Gestión Familiar</h1>", unsafe_allow_html=True)
    
    # Elegir usuario
    user = st.selectbox("¿Quién sos?", ["Seleccionar...", "Celeste", "Agu", "Mamá"])
    
    if user != "Seleccionar...":
        # ACÁ ESTABA EL ERROR: Cambié 'maxlength' por 'max_chars'
        pin = st.text_input(f"Hola {user}, ingresá tu PIN:", type="password", max_chars=4)
        
        if st.button("ENTRAR AL SISTEMA", use_container_width=True):
            if pin == usuarios.get(user):
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = user
                st.success("¡PIN Correcto!")
                st.rerun()
            else:
                st.error("PIN incorrecto. Revisalo.")

# --- PANTALLA PRINCIPAL ---
else:
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    st.write(f"## ¡Bienvenida, {st.session_state['usuario']}!")
    st.write("---")
    st.success("✅ PASO 1 COMPLETADO: Ya podés entrar con tu PIN.")
    
    st.write("### ¿Qué sigue ahora?")
    st.info("Ahora que ya entramos, tenemos que armar la calculadora de **Gastos del Mes** para sacar la **Meta Diaria**.")
