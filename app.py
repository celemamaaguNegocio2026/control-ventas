import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="celeagumama - Gestión", layout="centered")

# ID de tu Excel para LEER datos
ID_EXCEL = "1zcya1QAR3hnbddUruZSvfSkLATnM3XCvqrMndEY_UAg"
# URL de tu Formulario para ESCRIBIR datos (fijate que termina en /formResponse)
URL_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSdsxCKcF5JTe-_q0MxqV2PmKXlpuizVipmRywMSzfhmGNNrXQ/formResponse"

# --- FUNCIONES ---
def leer_hoja(nombre_hoja):
    url = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL}/gviz/tq?tqx=out:csv&sheet={nombre_hoja}"
    return pd.read_csv(url)

def enviar_venta_a_excel(usuario, monto, detalle):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    # Usamos los códigos entry que sacamos del formulario
    datos = {
        "entry.888769345": usuario,
        "entry.310360706": monto,
        "entry.685382042": detalle,
        "entry.444736630": fecha
    }
    try:
        requests.post(URL_FORM, data=datos)
        return True
    except:
        return False

# --- LOGIN ---
usuarios_fijos = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso Gestión Familiar")
    user = st.selectbox("¿Quién sos?", ["Seleccionar...", "Celeste", "Agu", "Mamá"])
    if user != "Seleccionar...":
        pin = st.text_input("PIN:", type="password", max_chars=4)
        if st.button("ENTRAR"):
            if pin == usuarios_fijos.get(user):
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = user
                st.rerun()

# --- PANTALLA PRINCIPAL ---
else:
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    menu = st.sidebar.radio("Ir a:", ["Cargar Ventas", "Configurar Metas"])

    if menu == "Configurar Metas":
        st.title("📊 Configuración de Gastos")
        st.info("Cargá los gastos para calcular tu meta del día.")
        alquiler = st.number_input("Alquiler:", value=0)
        luz = st.number_input("Luz/Servicios:", value=0)
        comida = st.number_input("Comida/Insumos:", value=0)
        sueldos = st.number_input("Sueldos:", value=0)
        
        total = alquiler + luz + comida + sueldos
        meta = total / 30
        st.session_state['meta_objetivo'] = meta
        
        st.metric("Meta Diaria Necesaria", f"${meta:,.2f}")

    elif menu == "Cargar Ventas":
        st.title("💰 Registro de Ventas")
        
        # Formulario de carga
        with st.container(border=True):
            monto_v = st.number_input("Monto de la venta ($):", min_value=0, step=100)
            detalle_v = st.text_input("¿Qué se vendió?")
            
            if st.button("🚀 Registrar Venta"):
                if monto_v > 0:
                    exito = enviar_venta_a_excel(st.session_state['usuario'], monto_v, detalle_v)
                    if exito:
                        st.success(f"¡Venta de ${monto_v} guardada en el Excel!")
                        st.balloons()
                    else:
                        st.error("Error al conectar con el Excel.")
                else:
                    st.warning("Poné un monto válido.")

        st.write("---")
        # Mostrar el progreso si hay meta configurada
        meta_hoy = st.session_state.get('meta_objetivo', 0)
        if meta_hoy > 0:
            st.subheader(f"Objetivo del día: ${meta_hoy:,.2f}")
            st.write("Andá a tu Excel para ver el listado completo de ventas.")
