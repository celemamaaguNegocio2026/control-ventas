import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Gestión Familiar MASTER", layout="wide")
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

def obtener_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=15)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def enviar_datos(p):
    try: return requests.post(URL_SCRIPT, params=p, timeout=15).status_code == 200
    except: return False

usuarios = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso")
    u = st.selectbox("Usuario:", ["Seleccionar..."] + list(usuarios.keys()))
    if u != "Seleccionar...":
        p = st.text_input("PIN:", type="password")
        if st.button("ENTRAR"):
            if p == usuarios[u]:
                st.session_state.update({"autenticado": True, "usuario": u}); st.rerun()
else:
    with st.spinner("Cargando balance real..."):
        d = obtener_datos()
        prods = d.get('productos', [])
        clis = d.get('clientes', [])
        envios = d.get('envios', [])
        bal = d.get('balance', {'ventasHoy': 0, 'gastosMes': 0})

    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    tabs = st.tabs(["💰 VENTAS", "📉 GASTOS", "👥 CLIENTES", "🛵 REPARTO", "📊 BALANCE"])

    with tabs[4]: # Pestaña Balance (NUEVA)
        st.header("Resumen del Negocio")
        col_b1, col_b2 = st.columns(2)
        
        meta_diaria = 30000 # Podés cambiar este número
        ventas_hoy = bal['ventasHoy']
        
        with col_b1:
            st.metric("Ventas de Hoy", f"${ventas_hoy}")
            progreso = min(ventas_hoy / meta_diaria, 1.0)
            st.write(f"Meta Diaria: ${meta_diaria}")
            st.progress(progreso)
            if progreso >= 1.0: st.success("¡META CUMPLIDA! 🏆")
        
        with col_b2:
            st.metric("Gastos Acumulados Mes", f"${bal['gastosMes']}", delta_color="inverse")
            st.info("Recordá que la ganancia real se calcula descontando los costos de mercadería en el Excel.")

    # ... (El resto de los tabs VENTAS, GASTOS, CLIENTES, REPARTO se mantienen como en la versión anterior) ...
    # Asegurate de mantener el código de las funciones de venta y envío que ya teníamos.

    # [CÓDIGO DE RELLENO PARA MANTENER LA APP FUNCIONAL]
    with tabs[0]: 
        st.subheader("Registrar Venta")
        nombres_p = [p['nombre'] for p in prods]
        sel_p = st.selectbox("Producto:", ["Manual"] + nombres_p)
        metodo = st.radio("Pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
        if st.button("GUARDAR VENTA"):
             if enviar_datos({"fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "usuario": st.session_state['usuario'], "monto": 100, "detalle": f"[{metodo}] Venta"}):
                 st.success("¡Listo!"); st.rerun()

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False; st.rerun()
