import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="celeagumama - Gestión", layout="centered")

# 1. ID de tu Excel (Para leer la meta y datos)
ID_EXCEL = "1zcya1QAR3hnbddUruZSvfSkLATnM3XCvqrMndEY_UAg"

# 2. URL de ENVÍO de tu Formulario (Corregida a /formResponse)
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSdsxCKcF5JTe-_q0MxqV2PmKXlpuizVipmRywMSzfhmGNNrXQ/formResponse"

# --- FUNCIONES ---
def leer_hoja(nombre_hoja):
    """Lee datos desde tu Google Sheet público"""
    url = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL}/gviz/tq?tqx=out:csv&sheet={nombre_hoja}"
    try:
        return pd.read_csv(url)
    except:
        return pd.DataFrame()

def enviar_venta_a_excel(usuario, monto, detalle):
    """Envía los datos al Excel a través del Google Form"""
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    # Estos son los códigos entry. que sacamos de tu formulario
    datos = {
        "entry.888769345": usuario,  # Pregunta: USUARIO
        "entry.310360706": monto,    # Pregunta: MONTO
        "entry.685382042": detalle,  # Pregunta: DETALLE
        "entry.444736630": fecha_hoy # Pregunta: FECHA
    }
    
    try:
        respuesta = requests.post(URL_FORM, data=datos)
        # Si el código es 200, es que Google recibió el paquete
        return respuesta.status_code == 200
    except:
        return False

# --- LÓGICA DE LOGIN ---
usuarios_fijos = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False
    st.session_state['usuario'] = ""

if not st.session_state['autenticado']:
    st.markdown("<h1 style='text-align: center;'>🔐 Gestión Familiar</h1>", unsafe_allow_html=True)
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
    menu = st.sidebar.radio("Menú:", ["Cargar Ventas", "Metas y Gastos"])
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    # --- SECCIÓN: CARGAR VENTAS ---
    if menu == "Cargar Ventas":
        st.title("💰 Registrar Nueva Venta")
        
        with st.container(border=True):
            monto_v = st.number_input("Monto vendido ($):", min_value=0, step=100, value=0)
            detalle_v = st.text_input("¿Qué vendiste? (Ej: 2 docenas de facturas)")
            
            if st.button("🚀 GUARDAR VENTA", use_container_width=True):
                if monto_v > 0:
                    with st.spinner("Guardando en Excel..."):
                        exito = enviar_venta_a_excel(st.session_state['usuario'], monto_v, detalle_v)
                    
                    if exito:
                        st.success(f"¡Genial {st.session_state['usuario']}! Se guardaron ${monto_v}")
                        st.balloons()
                    else:
                        st.error("Hubo un problema. Revisá que el link del formulario sea /formResponse")
                else:
                    st.warning("El monto debe ser mayor a 0")

        st.info("💡 Los datos aparecen en la pestaña 'Respuestas de formulario 1' de tu Excel.")

    # --- SECCIÓN: METAS Y GASTOS ---
    elif menu == "Metas y Gastos":
        st.title("📊 Calculadora de Metas")
        
        col1, col2 = st.columns(2)
        with col1:
            alquiler = st.number_input("Alquiler:", value=0)
            luz = st.number_input("Luz/Agua/Gas:", value=0)
        with col2:
            sueldos = st.number_input("Sueldos/Retiros:", value=0)
            otros = st.number_input("Insumos/Otros:", value=0)
        
        total_gastos = alquiler + luz + sueldos + otros
        meta_diaria = total_gastos / 30 if total_gastos > 0 else 0
        
        st.divider()
        st.metric("GASTOS TOTALES", f"${total_gastos:,.0f}")
        st.metric("META DIARIA (30 días)", f"${meta_diaria:,.2f}")
        
        if total_gastos > 0:
            st.warning(f"Necesitan vender **${meta_diaria:,.2f}** por día para cubrir todo.")
