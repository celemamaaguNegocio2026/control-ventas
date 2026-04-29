import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="celeagumama - Gestión", layout="centered")

# URLs actualizadas
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSdsxCKcF5JTe-_q0MxqV2PmKXlpuizVipmRywMSzfhmGNNrXQ/formResponse"

def enviar_venta_a_excel(usuario, monto, detalle):
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # ESTOS SON LOS CÓDIGOS QUE TU FORMULARIO TIENE AHORA:
    payload = {
        "entry.888769345": str(usuario),  # Para la pregunta USUARIO
        "entry.310360706": str(monto),    # Para la pregunta MONTO
        "entry.685382042": str(detalle),  # Para la pregunta DETALLE
        "entry.444736630": str(fecha_hoy) # Para la pregunta FECHA
    }
    
    try:
        # Enviamos los datos
        r = requests.post(URL_FORM, data=payload)
        return r.status_code == 200
    except:
        return False

# --- ACCESO ---
usuarios_fijos = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso Gestión Familiar")
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

# --- PANEL ---
else:
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    st.title("💰 Registrar Venta")
    
    with st.container(border=True):
        monto_v = st.number_input("Monto ($):", min_value=0, step=10)
        detalle_v = st.text_input("Detalle (Opcional):")
        
        if st.button("🚀 GUARDAR VENTA", use_container_width=True):
            if monto_v > 0:
                if enviar_venta_a_excel(st.session_state['usuario'], monto_v, detalle_v):
                    st.success(f"¡Venta de ${monto_v} enviada! Chequeá el Excel.")
                    st.balloons()
                else:
                    st.error("Hubo un error de conexión.")
            else:
                st.warning("El monto debe ser mayor a 0.")
