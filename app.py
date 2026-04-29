import streamlit as st

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="celeagumama - Gestión", layout="centered")

# Simulación de los datos del Excel (Después conectaremos el Sheets real)
usuarios = {
    "Celeste": "1234", # Cambiá estos números por los que quieras
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
    user = st.selectbox("¿Quién sos?", ["Seleccioná...", "Celeste", "Agu", "Mamá"])
    
    if user != "Seleccionar...":
        # Entrada de PIN
        pin = st.text_input(f"Hola {user}, ingresá tu PIN:", type="password", maxlength=4)
        
        if st.button("ENTRAR AL SISTEMA", use_container_width=True):
            if pin == usuarios.get(user):
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = user
                st.success("Acceso concedido. Cargando...")
                st.rerun()
            else:
                st.error("PIN incorrecto. Revisalo.")

# --- PANTALLA PRINCIPAL (Solo se ve si el PIN es correcto) ---
else:
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    st.write(f"## ¡Bienvenida, {st.session_state['usuario']}!")
    st.write("---")
    st.info("✅ PASO 1 COMPLETADO: Acceso y Seguridad.")
    
    # Aquí es donde vamos a poner el PASO 2
    st.write("### ¿Qué sigue ahora?")
    st.write("Elegí el siguiente paso:")
    st.button("📦 Configurar Inventario y Costos")
    st.button("💰 Cargar Gastos Mensuales (Para calcular la Meta)")
