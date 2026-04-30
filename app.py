import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Gestión Familiar Ultra", layout="wide")

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

# --- FUNCIONES ---
def obtener_productos():
    try:
        r = requests.get(URL_SCRIPT, timeout=10)
        return r.json() if r.status_code == 200 else []
    except: return []

def enviar_datos(payload):
    try:
        r = requests.post(URL_SCRIPT, params=payload, timeout=15)
        return r.status_code == 200
    except: return False

# --- LOGIN ---
usuarios = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso")
    u = st.selectbox("Usuario:", ["Seleccionar..."] + list(usuarios.keys()))
    if u != "Seleccionar...":
        p = st.text_input("PIN:", type="password")
        if st.button("ENTRAR"):
            if p == usuarios[u]:
                st.session_state.update({"autenticado": True, "usuario": u})
                st.rerun()
else:
    # --- PANEL PRINCIPAL ---
    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    
    # META DIARIA (Ejemplo: $50.000)
    meta_objetivo = 50000 
    venta_actual = 0 # Esto lo conectaremos al Excel después para que sea real
    
    st.subheader("📊 Meta Diaria")
    progreso = min(venta_actual / meta_objetivo, 1.0)
    st.progress(progreso)
    st.write(f"Vendido: ${venta_actual} / Objetivo: ${meta_objetivo}")

    tab1, tab2 = st.tabs(["💰 VENTAS", "📉 GASTOS"])

    with tab1:
        with st.spinner("Cargando productos..."):
            prods = obtener_productos()
        
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown("### Registrar Venta")
            nombres = [p['nombre'] for p in prods]
            sel = st.selectbox("Producto:", ["Manual"] + nombres)
            
            monto = 0
            prod_nombre = ""
            if sel == "Manual":
                monto = st.number_input("Monto ($):", min_value=0)
                desc = st.text_input("Detalle:")
            else:
                p_data = next(item for item in prods if item['nombre'] == sel)
                monto = st.number_input("Precio ($):", value=int(float(p_data['venta'])))
                desc = f"Venta: {sel}"
                prod_nombre = sel
                st.caption(f"Stock: {p_data['stock']}")

            metodo = st.radio("Pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
            
            if st.button("GUARDAR VENTA"):
                payload = {
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario": st.session_state['usuario'],
                    "monto": monto,
                    "detalle": f"[{metodo}] {desc}",
                    "producto_nombre": prod_nombre
                }
                if enviar_datos(payload):
                    st.success("¡Venta guardada!"); st.balloons()
        
        with col_v2:
            st.markdown("### Consumo Casa")
            if nombres:
                c_sel = st.selectbox("Qué sacaron?", nombres)
                if st.button("DESCONTAR DE STOCK"):
                    payload = {
                        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        "usuario": st.session_state['usuario'],
                        "monto": 0,
                        "detalle": f"CONSUMO CASA: {c_sel}",
                        "producto_nombre": c_sel
                    }
                    if enviar_datos(payload): st.warning("Stock actualizado")

    with tab2:
        st.subheader("Registro de Gastos")
        with st.container(border=True):
            cat = st.selectbox("Categoría:", ["Mercadería", "Luz/Servicios", "Alquiler", "Sueldos", "Otros"])
            monto_g = st.number_input("Monto Gasto ($):", min_value=0)
            det_g = st.text_input("Detalle del gasto:")
            
            if st.button("REGISTRAR GASTO"):
                payload_g = {
                    "tipo": "gasto",
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario": st.session_state['usuario'],
                    "categoria": cat,
                    "monto": monto_g,
                    "detalle": det_g
                }
                if enviar_datos(payload_g):
                    st.error(f"Gasto de ${monto_g} anotado.")
                    st.rerun()

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()
