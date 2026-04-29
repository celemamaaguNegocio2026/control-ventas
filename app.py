import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="celeagumama - Gestión", layout="centered")

# 1. Identificadores de Google (Copiados de tus links)
ID_EXCEL = "1zcya1QAR3hnbddUruZSvfSkLATnM3XCvqrMndEY_UAg"
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSdsxCKcF5JTe-_q0MxqV2PmKXlpuizVipmRywMSzfhmGNNrXQ/formResponse"

# --- FUNCIONES ---
def enviar_venta_a_excel(usuario, monto, detalle):
    """Envía los datos al Excel a través del Google Form"""
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # IDs de las preguntas (entries) verificados de tu link
    datos = {
        "entry.888769345": str(usuario),  # Usuario
        "entry.310360706": str(monto),    # Monto
        "entry.685382042": str(detalle),  # Detalle
        "entry.444736630": str(fecha_hoy) # Fecha
    }
    
    try:
        # Enviamos la petición y verificamos que Google responda OK
        respuesta = requests.post(URL_FORM, data=datos)
        return respuesta.status_code == 200
    except:
        return False

# --- LÓGICA DE ACCESO ---
usuarios_fijos = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Control de Ventas</h2>", unsafe_allow_html=True)
    user = st.selectbox("Seleccioná tu nombre:", ["Seleccionar...", "Celeste", "Agu", "Mamá"])
    
    if user != "Seleccionar...":
        pin = st.text_input(f"PIN de {user}:", type="password", max_chars=4)
        if st.button("INGRESAR", use_container_width=True):
            if pin == usuarios_fijos.get(user):
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = user
                st.rerun()
            else:
                st.error("PIN incorrecto")

# --- PANEL PRINCIPAL ---
else:
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    opcion = st.sidebar.radio("Menú:", ["Cargar Venta", "Ver Gastos y Metas"])
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    if opcion == "Cargar Venta":
        st.title("💰 Registro de Venta Diaria")
        
        with st.container(border=True):
            monto_v = st.number_input("Monto en pesos ($):", min_value=0, step=100, value=0)
            detalle_v = st.text_input("Comentario (Opcional):", placeholder="Ej: Venta panadería")
            
            if st.button("🚀 REGISTRAR AHORA", use_container_width=True):
                if monto_v > 0:
                    with st.spinner("Conectando con Google Sheets..."):
                        if enviar_venta_a_excel(st.session_state['usuario'], monto_v, detalle_v):
                            st.success(f"¡Excelente! Venta de ${monto_v} registrada.")
                            st.balloons()
                        else:
                            st.error("No se pudo guardar. Revisá la conexión.")
                else:
                    st.warning("Ingresá un monto mayor a cero.")

    elif opcion == "Ver Gastos y Metas":
        st.title("📊 Calculadora de Negocio")
        c1, c2 = st.columns(2)
        with c1:
            g1 = st.number_input("Alquiler:", value=0)
            g2 = st.number_input("Servicios (Luz/Gas):", value=0)
        with c2:
            g3 = st.number_input("Sueldos/Retiros:", value=0)
            g4 = st.number_input("Otros Gastos:", value=0)
        
        total = g1 + g2 + g3 + g4
        meta = total / 30
        
        st.divider()
        st.subheader(f"Gastos Mensuales: ${total:,.2f}")
        st.info(f"🎯 **Meta para cubrir gastos:** Deben vender **${meta:,.2f}** por día.")
