import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="celeagumama - Gestión", layout="centered")

# --- PASO 1: BASE DE DATOS DE USUARIOS ---
# Ya puse tus PINs: 1997, 1995 y 1975
usuarios = {
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
    
    # Elegir usuario
    user = st.selectbox("¿Quién sos?", ["Seleccionar...", "Celeste", "Agu", "Mamá"])
    
    if user != "Seleccionar...":
        # Entrada de PIN
        pin = st.text_input(f"Hola {user}, ingresá tu PIN de 4 dígitos:", type="password", max_chars=4)
        
        if st.button("ENTRAR AL SISTEMA", use_container_width=True):
            if pin == usuarios.get(user):
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = user
                st.success("¡PIN Correcto! Entrando...")
                st.rerun()
            else:
                st.error("PIN incorrecto. Revisá el año que elegiste.")

# --- PANTALLA PRINCIPAL (Solo se ve si el PIN es correcto) ---
else:
    # Barra lateral con saludo y botón de salida
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    st.write(f"## ¡Bienvenida, {st.session_state['usuario']}!")
    st.write("---")
    
    # Marcamos el Paso 1 como listo
    st.success("✅ PASO 1: Acceso y Seguridad COMPLETADO.")
    
    # --- PREPARACIÓN PASO 2: GASTOS Y META ---
    st.write("### 🚀 PASO 2: Definir Gastos y Meta")
    st.write("Ahora necesitamos saber cuánto hay que pagar este mes para calcular la meta diaria.")
    
    with st.expander("📊 Cargar Gastos Mensuales (Alquiler, Luz, Sueldos)"):
        st.write("Cargá los montos aproximados de este mes:")
        alquiler = st.number_input("Alquiler:", min_value=0, value=0)
        luz = st.number_input("Luz/Servicios:", min_value=0, value=0)
        comida = st.number_input("Comida Negocio/Casa:", min_value=0, value=0)
        sueldos = st.number_input("Sueldos (Total de las 3):", min_value=0, value=0)
        
        total_gastos = alquiler + luz + comida + sueldos
        
        if total_gastos > 0:
            st.warning(f"Total de gastos este mes: ${total_gastos}")
            meta_diaria = total_gastos / 30
            st.info(f"Para cubrir esto, la meta diaria mínima es: **${meta_diaria:,.2f}**")
            
            if st.button("Guardar Gastos y Meta"):
                st.success("¡Meta guardada! (Esto se guardará en tu Excel en el siguiente paso)")
