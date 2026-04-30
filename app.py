import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Gestión Familiar Business", layout="wide")

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

def obtener_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=15)
        if r.status_code == 200:
            return r.json()
        return {"productos": [], "clientes": [], "envios": []}
    except: return {"productos": [], "clientes": [], "envios": []}

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
    with st.spinner("Sincronizando..."):
        datos = obtener_datos()
        prods = datos.get('productos', [])
        clis = datos.get('clientes', [])
        envios = datos.get('envios', [])

    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    
    tabs = st.tabs(["💰 VENTAS", "📉 GASTOS", "👥 CLIENTES", "🛵 REPARTO"])

    with tabs[0]: # VENTAS
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.subheader("Registrar Venta")
            nombres_p = [p['nombre'] for p in prods]
            sel_p = st.selectbox("Producto:", ["Manual"] + nombres_p)
            
            monto = 0
            if sel_p == "Manual":
                monto = st.number_input("Monto ($):", min_value=0, key="m_man")
                desc = st.text_input("Detalle:", key="d_man")
            else:
                p_data = next(item for item in prods if item['nombre'] == sel_p)
                try:
                    precio_sugerido = int(float(str(p_data.get('venta', '0')).replace(',', '.')))
                except: precio_sugerido = 0
                monto = st.number_input("Precio ($):", value=precio_sugerido)
                desc = f"Venta: {sel_p}"

            metodo = st.radio("Pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
            cliente_sel = st.selectbox("Cliente:", [c['nombre'] for c in clis]) if metodo == "Fiado" else ""
            
            es_envio = st.checkbox("¿Es para enviar a domicilio?")
            direccion = st.text_input("Dirección de entrega:") if es_envio else ""

            if st.button("🚀 GUARDAR"):
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
                    st.success("¡Guardado!"); st.rerun()

    with tabs[1]: # GASTOS
        st.subheader("Registrar Gasto")
        cat = st.selectbox("Categoría:", ["Mercadería", "Servicios", "Alquiler", "Sueldos", "Otros"])
        m_g = st.number_input("Monto ($):", min_value=0, key="g_m")
        if st.button("ANOTAR GASTO"):
            if enviar_datos({"tipo": "gasto", "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "usuario": st.session_state['usuario'], "categoria": cat, "monto": m_g, "detalle": "Gasto"}):
                st.rerun()

    with tabs[2]: # CLIENTES
        st.subheader("Saldos de Clientes")
        for c in clis:
            saldo = float(c.get('saldo', 0))
            if saldo > 0:
                with st.expander(f"🔴 {c['nombre']} - DEBE: ${saldo}"):
                    pago = st.number_input("Monto que paga:", min_value=0, max_value=int(saldo), key=f"p_{c['nombre']}")
                    if st.button("COBRAR", key=f"b_{c['nombre']}"):
                        if enviar_datos({"tipo": "cobro", "cliente": c['nombre'], "monto": pago}): st.rerun()

    with tabs[3]: # REPARTO
        st.subheader("📦 Pedidos Pendientes")
        if not envios:
            st.info("No hay pedidos para entregar.")
        else:
            for e in envios:
                with st.container(border=True):
                    st.write(f"**Cliente:** {e['cliente']}")
                    st.write(f"🏠 {e['direccion']}")
                    st.write(f"💰 Cobrar: **${e['total']}**")
                    if st.button(f"Marcar como ENTREGADO", key=f"env_{e['id']}"):
                        if enviar_datos({"tipo": "estado_envio", "id": e['id']}):
                            st.success("¡Pedido entregado!"); st.rerun()

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False; st.rerun()
