import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión de Ventas", layout="centered")

# URL de tu NUEVO formulario (ya corregida con /formResponse)
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScRpTme1PM3g5t1soKW_2evI7-EjUCLX7Ya3_UpGnSor_Z5Eg/formResponse"

def enviar_venta_a_excel(usuario, monto, detalle):
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # NUEVOS CÓDIGOS sacados de tu último formulario
    payload = {
        "entry.2069796014": str(usuario), # Código para USUARIO
        "entry.1843577747": str(monto),   # Código para MONTO
        "entry.473551532": str(detalle),  # Código para DETALLE
        "entry.1693892789": str(fecha_hoy) # Código para FECHA
    }
    
    try:
        # Enviamos los datos a Google
        r = requests.post(URL_FORM, data=payload)
        return r.status_code == 200
    except:
        return False

# --- ACCESO ---
usuarios_fijos = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso Familiar")
    user = st.selectbox("¿Quién sos?", ["Seleccionar...", "Celeste", "Agu", "Mamá"])
    if user != "Seleccionar...":
        pin = st.text_input(f"PIN de {user}:", type="password", max_chars=4)
        if st.button("ENTRAR", use_container_width=True):
            if pin == usuarios_fijos.get(user):
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = user
                st.rerun()
            else:
                st.error("PIN incorrecto")

# --- PANEL DE CARGA ---
else:
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    st.title("💰 Registrar Venta")
    
    with st.container(border=True):
        monto_v = st.number_input("Monto ($):", min_value=0, step=10, value=0)
        detalle_v = st.text_input("¿Qué se vendió?")
        
        if st.button("🚀 GUARDAR EN EXCEL", use_container_width=True):
            if monto_v > 0:
                with st.spinner("Subiendo datos..."):
                    if enviar_venta_a_excel(st.session_state['usuario'], monto_v, detalle_v):
                        st.success(f"¡Venta de ${monto_v} guardada correctamente!")
                        st.balloons()
                    else:
                        st.error("Error al conectar con Google. Revisá el formulario.")
            else:
                st.warning("Ingresá un monto válido.")

    st.info("Recordá vincular este nuevo formulario a tu Excel desde la pestaña 'Respuestas' del formulario.")
