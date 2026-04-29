import streamlit as st
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="celeagumama - Gestión", layout="centered")
ID_EXCEL = "1zcya1QAR3hnbddUruZSvfSkLATnM3XCvqrMndEY_UAg"

def leer_hoja(nombre_hoja):
    url = f"https://docs.google.com/spreadsheets/d/{ID_EXCEL}/gviz/tq?tqx=out:csv&sheet={nombre_hoja}"
    return pd.read_csv(url)

# --- LOGIN ---
usuarios_fijos = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso Gestión Familiar")
    user = st.selectbox("¿Quién sos?", ["Seleccionar...", "Celeste", "Agu", "Mamá"])
    if user != "Seleccionar...":
        pin = st.text_input(f"Hola {user}, PIN:", type="password", max_chars=4)
        if st.button("ENTRAR"):
            if pin == usuarios_fijos.get(user):
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = user
                st.rerun()
            else:
                st.error("PIN incorrecto")

# --- PANTALLA PRINCIPAL ---
else:
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()

    st.title("📊 Panel de Gastos y Metas")
    
    # --- FORMULARIO DE GASTOS ---
    with st.container(border=True):
        st.subheader("📝 Cargar Gastos del Mes")
        col1, col2 = st.columns(2)
        
        with col1:
            alquiler = st.number_input("Alquiler ($):", min_value=0, step=1000)
            luz = st.number_input("Luz/Servicios ($):", min_value=0, step=100)
        
        with col2:
            comida = st.number_input("Insumos/Comida ($):", min_value=0, step=500)
            sueldos = st.number_input("Sueldos (Total):", min_value=0, step=1000)

        total_gastos = alquiler + luz + comida + sueldos
        
        st.divider()
        
        if total_gastos > 0:
            st.metric("TOTAL GASTOS MES", f"${total_gastos:,.0f}")
            
            # Cálculo de Meta (dividido 26 días laborables o 30, usemos 30 para ser conservadores)
            meta_diaria = total_gastos / 30
            
            st.warning(f"🎯 **Meta Diaria Sugerida:** ${meta_diaria:,.2f}")
            st.info("Esta es la venta mínima necesaria por día para cubrir todo.")

            if st.button("💾 Guardar y Actualizar Meta"):
                st.success("¡Meta actualizada! (En el próximo paso haremos que se escriba sola en el Excel)")

    st.write("---")
    st.write("### 🪜 ¿Qué falta?")
    st.write("Ahora que podés ver los gastos, ¿querés que armemos la parte de **'Cargar Venta Diaria'**? Así cada vez que vendan algo, la App les diga cuánto falta para llegar a la meta del día.")
