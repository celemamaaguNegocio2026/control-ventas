import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="celeagumama - Gestión", layout="centered")

# 1. ID de tu Excel (Para leer datos si fuera necesario)
ID_EXCEL = "1zcya1QAR3hnbddUruZSvfSkLATnM3XCvqrMndEY_UAg"

# 2. URL de ENVÍO de tu Formulario (Debe terminar en /formResponse)
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSdsxCKcF5JTe-_q0MxqV2PmKXlpuizVipmRywMSzfhmGNNrXQ/formResponse"

# --- FUNCIONES ---
def enviar_venta_a_excel(usuario, monto, detalle):
    """Envía los datos al Excel a través del Google Form"""
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Estos son los códigos entry de tu formulario actual
    # Los enviamos como strings para que Google los acepte siempre
    datos = {
        "entry.888769345": str(usuario),
        "entry.310360706": str(monto),
        "entry.685382042": str(detalle),
        "entry.444736630": str(fecha_hoy)
    }
    
    try:
        # Simulamos que somos un navegador para evitar bloqueos
        headers = {'Referer': URL_FORM, 'User-Agent': "Mozilla/5.0"}
        respuesta = requests.post(URL_FORM, data=datos, headers=headers)
        return respuesta.status_code == 200
    except:
        return False

# --- LÓGICA DE LOGIN ---
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

# --- PANTALLA PRINCIPAL (LOGUEADO) ---
else:
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    menu = st.sidebar.radio("Ir a:", ["Cargar Ventas", "Configurar Metas"])
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    if menu == "Cargar Ventas":
        st.title("💰 Registro de Ventas")
        
        with st.container(border=True):
            monto_v = st.number_input("Monto de la venta ($):", min_value=0, step=10, value=0)
            detalle_v = st.text_input("¿Qué se vendió?")
            
            if st.button("🚀 REGISTRAR VENTA", use_container_width=True):
                if monto_v > 0:
                    with st.spinner("Guardando en la nube..."):
                        exito = enviar_venta_a_excel(st.session_state['usuario'], monto_v, detalle_v)
                    
                    if exito:
                        st.success(f"¡Hecho! Se guardó la venta de ${monto_v}")
                        st.balloons()
                    else:
                        st.error("Error técnico al guardar. Avisame si persiste.")
                else:
                    st.warning("El monto debe ser mayor a 0.")

        st.info("Recordá que podés ver el listado total en la pestaña 'Respuestas de formulario 1' de tu Excel.")

    elif menu == "Configurar Metas":
        st.title("📊 Configuración de Gastos")
        alquiler = st.number_input("Alquiler:", value=0)
        luz = st.number_input("Luz/Servicios:", value=0)
        sueldos = st.number_input("Sueldos/Retiros:", value=0)
        insumos = st.number_input("Insumos:", value=0)
        
        total = alquiler + luz + sueldos + insumos
        meta = total / 30
        
        st.divider()
        st.metric("TOTAL GASTOS", f"${total:,.2f}")
        st.metric("META DIARIA", f"${meta:,.2f}")
