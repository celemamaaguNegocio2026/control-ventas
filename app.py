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
        return {"productos": [], "clientes": [], "envios": [], "balance": {"ventasHoy": 0, "gastosMes": 0, "gananciaEstimadaHoy": 0}}
    except: 
        return {"productos": [], "clientes": [], "envios": [], "balance": {"ventasHoy": 0, "gastosMes": 0, "gananciaEstimadaHoy": 0}}

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
        bal = d.get('balance', {})

    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    tabs = st.tabs(["💰 VENTAS", "📉 GASTOS", "👥 CLIENTES", "🛵 REPARTO", "📊 BALANCE"])

    # --- TAB 1: VENTAS ---
    with tabs[0]:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.subheader("Registrar Venta")
            nombres_p = [p['nombre'] for p in prods]
            sel_p = st.selectbox("Producto:", ["Manual"] + nombres_p)
            
            if sel_p == "Manual":
                monto = st.number_input("Monto ($):", min_value=0, key="m_man")
                desc = st.text_input("Detalle:", key="d_man")
                prod_nombre_stock = ""
            else:
                p_data = next(item for item in prods if item['nombre'] == sel_p)
                try:
                    precio_sug = int(float(str(p_data.get('venta', '0')).replace(',', '.')))
                except: precio_sug = 0
                monto = st.number_input("Precio ($):", value=precio_sug, key="m_p_val")
                desc = f"Venta: {sel_p}"
                prod_nombre_stock = sel_p
                st.caption(f"Stock actual: {p_data.get('stock', 0)}")

            metodo = st.radio("Pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
            cliente_sel = st.selectbox("Cliente:", [c['nombre'] for c in clis]) if metodo == "Fiado" else ""
            
            es_envio = st.checkbox("¿Es para enviar?")
            direccion = st.text_input("Dirección de entrega:") if es_envio else ""

            if st.button("🚀 GUARDAR VENTA"):
                payload = {
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario": st.session_state['usuario'],
                    "monto": monto,
                    "detalle": f"[{metodo}] {desc}",
                    "producto_nombre": prod_nombre_stock,
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
        if not clis:
            st.info("No hay clientes cargados.")
        for c in clis:
            saldo = float(c.get('saldo', 0))
            if saldo > 0:
                with st.expander(f"🔴 {c['nombre']} - DEBE: ${saldo}"):
                    pago = st.number_input(f"Monto que paga {c['nombre']}:", min_value=0, max_value=int(saldo), key=f"p_{c['nombre']}")
                    if st.button(f"Cobrar a {c['nombre']}", key=f"b_{c['nombre']}"):
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
                    st.write(f"**Cliente:** {e['cliente']} | **Cobrar:** ${e['total']}")
                    st.write(f"🏠 {e['direccion']}")
                    if st.button(f"Marcar Entregado", key=f"env_{e['id']}"):
                        if enviar_datos({"tipo": "estado_envio", "id": e['id']}):
                            st.rerun()

    # --- TAB 5: BALANCE ---
    with tabs[4]:
        st.header("📊 Balance y Ganancia Real")
        
        ventas_hoy = bal.get('ventasHoy', 0)
        ganancia_bruta = bal.get('gananciaEstimadaHoy', 0)
        ahorro_emergencia = ventas_hoy * 0.05
        disponible = ventas_hoy - ahorro_emergencia

        col_met1, col_met2, col_met3 = st.columns(3)
        with col_met1:
            st.metric("Ventas de Hoy", f"${ventas_hoy}")
        with col_met2:
            st.metric("Reserva (5%)", f"${ahorro_emergencia:.2f}")
        with col_met3:
            st.metric("Caja Disponible", f"${disponible:.2f}")

        st.divider()
        
        # Reparto del Plus
        meta_reparto = 30000
        if ventas_hoy > meta_reparto:
            sobrante = ventas_hoy - meta_reparto
            cada_una = sobrante / 3
            st.balloons()
            st.success(f"¡Meta superada! Plus de **${cada_una:.2f}** para cada una.")
        else:
            st.warning(f"Faltan ${meta_reparto - ventas_hoy} para llegar al plus.")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False; st.rerun()
