import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión de Ventas", layout="centered")

# URL base de tu NUEVO formulario
URL_BASE = "https://docs.google.com/forms/d/e/1FAIpQLScRpTme1PM3g5t1soKW_2evI7-EjUCLX7Ya3_UpGnSor_Z5Eg/formResponse"

def enviar_venta_a_excel(usuario, monto, detalle):
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Armamos la URL con los datos pegados al final (esto no falla)
    # entry.2069796014 -> USUARIO
    # entry.1843577747 -> MONTO
    # entry.473551532  -> DETALLE
    # entry.1693892789 -> FECHA
    
    url_final = (
        f"{URL_BASE}?"
        f"entry.2069796014={usuario}&"
        f"entry.1843577747={monto}&"
        f"entry.473551532={detalle}&"
        f"entry.1693892789={fecha_hoy}&"
        f"submit=Submit"
    )
    
    try:
        # Usamos GET en lugar de POST para "empujar" los datos por la URL
        r = requests.get(url_final)
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
                # Limpiamos el detalle de espacios o caracteres raros
                detalle_limpio = detalle_v.replace(" ", "+")
                if enviar_venta_a_excel(st.session_state['usuario'], monto_v, detalle_limpio):
                    st.success(f"¡Venta de ${monto_v} enviada!")
                    st.balloons()
                else:
                    st.error("Error al enviar.")
            else:
                st.warning("Ingresá un monto.")
