import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión Familiar", layout="centered")

# URL de tu Google Apps Script (La que me pasaste recién)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

def enviar_datos_directo(usuario, monto, detalle):
    """Envía los datos directamente al corazón del Excel vía Apps Script"""
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Armamos el paquete de datos
    payload = {
        "fecha": fecha_hoy,
        "usuario": usuario,
        "monto": monto,
        "detalle": detalle
    }
    
    try:
        # Enviamos por POST al script de Google
        # Usamos 'timeout' para que no se quede colgado si internet falla
        respuesta = requests.post(URL_SCRIPT, params=payload, timeout=10)
        return respuesta.status_code == 200
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return False

# --- LÓGICA DE ACCESO (LOGIN) ---
usuarios_fijos = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso Gestión</h2>", unsafe_allow_html=True)
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

# --- PANEL DE REGISTRO (LOGUEADO) ---
else:
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    st.title("💰 Registrar Venta")
    st.write("Cargá los datos y apretá el botón para guardar en el Excel.")
    
    with st.container(border=True):
        monto_v = st.number_input("Monto de la venta ($):", min_value=0, step=10, value=0)
        detalle_v = st.text_input("¿Qué se vendió? (Opcional):", placeholder="Ej: Pan, Facturas, etc.")
        
        if st.button("🚀 GUARDAR EN EXCEL", use_container_width=True):
            if monto_v > 0:
                with st.spinner("Guardando en la nube..."):
                    exito = enviar_datos_directo(st.session_state['usuario'], monto_v, detalle_v)
                
                if exito:
                    st.success(f"¡Venta de ${monto_v} registrada con éxito!")
                    st.balloons()
                else:
                    st.error("No se pudo guardar. Revisá si la pestaña del Excel se llama VENTAS.")
            else:
                st.warning("Por favor, ingresá un monto mayor a 0.")

    st.divider()
    st.info("💡 Tip: Los datos aparecen al final de la hoja 'VENTAS' en tu Google Sheet.")
