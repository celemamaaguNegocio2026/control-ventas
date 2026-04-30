import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Familiar MASTER", layout="wide")
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

def obtener_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=15)
        if r.status_code == 200:
            return r.json()
        return {"productos": [], "clientes": [], "envios": [], "balance": {"ventasHoy": 0, "gastosMes": 0}}
    except: 
        return {"productos": [], "clientes": [], "envios": [], "balance": {"ventasHoy": 0, "gastosMes": 0}}

def enviar_datos(payload):
    try:
        r = requests.post(URL_SCRIPT, params=payload, timeout=15)
        return r.status_code == 200
    except: 
        return False

# --- LOGIN ---
usuarios = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
if 'autenticado' not in st.session_state: 
    st.session_state['autenticado'] = False

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
                st.error("PIN Incorrecto")
else:
    # --- CARGA DE DATOS ---
    with st.spinner("Sincronizando datos..."):
        d = obtener_datos()
        prods = d.get('productos', [])
        clis = d.get('clientes', [])
        envios = d.get('envios', [])
        bal = d.get('balance', {'ventasHoy': 0, 'gastosMes': 0})

    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    tabs = st.tabs(["💰 VENTAS", "📉 GASTOS", "👥 CLIENTES", "🛵 REPARTO", "📊 BALANCE"])

    # --- TAB 1: VENTAS ---
    with tabs[0]:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.subheader("Registrar Venta")
            nombres_p = [p['nombre'] for p in prods]
            sel_p = st.selectbox("Producto:", ["Manual"] + nombres_p)
            
            monto = 0
            desc = ""
            if sel_p == "Manual":
                monto = st.number_input("Monto ($):", min_value=0, key="m_man")
                desc = st.text_input("Detalle:", key="d_man")
            else:
                p_data = next(item for item in prods if item['nombre'] == sel_p)
                try:
                    precio_sug = int(float(str(p_data.get('venta', '0')).replace(',', '.')))
                except: precio_sug = 0
                monto = st.number_input("Precio ($):", value=precio_sug, key="m_p_val")
                desc = f"Venta: {sel_p}"
                st.caption(f"Stock: {p_data.get('stock', 0)}")

            metodo = st.radio("Pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
            cliente_sel = st.selectbox("Cliente:", [c['nombre'] for c in clis]) if metodo == "Fiado" else ""
            
            es_envio = st.checkbox("¿Es para enviar?")
            direccion = st.text_input("Dirección:") if es_envio else ""

            if st.button("🚀 GUARDAR VENTA"):
                payload = {
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario": st.session_state['usuario'],
                    "monto": monto,
                    "detalle": f"[{metodo}] {desc}",
                    "producto_nombre": "" if sel_p == "Manual" else sel_p,
                    "metodo": metodo,
                    "cliente": cliente_sel
                }
                if enviar_datos(payload):
                    if es_envio:
                        enviar_datos({"tipo": "envio", "fecha": payload["fecha"], "cliente": cliente_sel if cliente_sel else "Venta Mostrador", "direccion": direccion, "total": monto})
                    st.success("¡Venta Guardada!"); st.rerun()

    # --- TAB 2: GASTOS ---
    with tabs[1]:
        st.subheader("Registrar Gasto")
        cat = st.selectbox("Categoría:", ["Mercadería", "Servicios", "Alquiler", "Sueldos", "Otros"])
        m_g = st.number_input("Monto ($):", min_value=0, key="g_m_val")
        det_g = st.text_input("Detalle del gasto:", key="g_d_val")
        if st.button("ANOTAR GASTO"):
            if enviar_datos({"tipo": "gasto", "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "usuario": st.session_state['usuario'], "categoria": cat, "monto": m_g, "detalle": det_g}):
                st.success("Gasto registrado"); st.rerun()

    # --- TAB 3: CLIENTES ---
    with tabs[2]:
        st.subheader("Cuentas Pendientes")
        for c in clis:
            saldo = float(c.get('saldo', 0))
            if saldo > 0:
                with st.expander(f"🔴 {c['nombre']} - DEBE: ${saldo}"):
                    pago = st.number_input(f"Monto que paga {c['nombre']}:", min_value=0, max_value=int(saldo), key=f"p_{c['nombre']}")
                    if st.button(f"Cobrar", key=f"b_{c['nombre']}"):
                        if enviar_datos({"tipo": "cobro", "cliente": c['nombre'], "monto": pago}): 
                            st.success("Cobro realizado"); st.rerun()
            else:
                st.write(f"🟢 {c['nombre']} está al día.")

    # --- TAB 4: REPARTO ---
    with tabs[3]:
        st.subheader("📦 Pedidos Pendientes")
        if not envios:
            st.info("No hay pedidos pendientes.")
        else:
            for e in envios:
                with st.container(border=True):
                    st.write(f"**Cliente:** {e['cliente']} | **Monto:** ${e['total']}")
                    st.write(f"🏠 {e['direccion']}")
                    if st.button(f"Entregado", key=f"env_{e['id']}"):
                        if enviar_datos({"tipo": "estado_envio", "id": e['id']}):
                            st.rerun()

    # --- TAB 5: BALANCE ---
    with tabs[4]:
        st.header("Estado del Negocio")
        meta_diaria = 30000 
        ventas_hoy = bal.get('ventasHoy', 0)
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.metric("Ventas de Hoy", f"${ventas_hoy}")
            prog = min(ventas_hoy / meta_diaria, 1.0) if meta_diaria > 0 else 0
            st.progress(prog)
            st.caption(f"Meta: ${meta_diaria}")
        
        with col_b2:
            st.metric("Gastos del Mes", f"${bal.get('gastosMes', 0)}")
            st.write("---")
            st.write("**Ganancia Estimada:** Se calcula en el Excel restando costos de productos.")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False; st.rerun()
