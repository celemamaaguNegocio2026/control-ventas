import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión MASTER Pro", layout="centered", initial_sidebar_state="expanded")

# CSS para asegurar que el teclado funcione y el diseño sea limpio en móvil
st.markdown("""
    <style>
    input { font-size: 16px !important; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
    .stMetric { background-color: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #eee; }
    </style>
    """, unsafe_allow_html=True)

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

# --- FUNCIONES DE DATOS ---
def obtener_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=10)
        if r.status_code == 200:
            datos = r.json()
            st.session_state['backup'] = datos
            return datos
        return st.session_state.get('backup', {})
    except:
        return st.session_state.get('backup', {"productos":[], "clientes":[], "balance":{}, "envios":[]})

def enviar_datos(payload):
    try:
        r = requests.post(URL_SCRIPT, params=payload, timeout=10)
        return r.status_code == 200
    except: return False

# --- INICIALIZACIÓN DE ESTADOS ---
if 'items_venta' not in st.session_state: st.session_state['items_venta'] = []
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False

# --- LOGIN ---
if not st.session_state['autenticado']:
    st.title("🔐 Acceso")
    u = st.selectbox("Usuario:", ["Seleccionar...", "Celeste", "Agu", "Mamá"])
    p = st.text_input("PIN:", type="password")
    if st.button("INGRESAR"):
        pins = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
        if p == pins.get(u):
            st.session_state.update({"autenticado": True, "usuario": u})
            st.rerun()
        else: st.error("PIN incorrecto")

else:
    datos = obtener_datos()
    
    # --- MENÚ LATERAL ---
    with st.sidebar:
        st.title(f"👋 {st.session_state['usuario']}")
        menu = st.radio("IR A:", ["💰 Ventas", "👥 Clientes", "🛵 Repartos", "📊 Balance"])
        st.divider()
        if st.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()

    # --- SECCIÓN VENTAS ---
    if menu == "💰 Ventas":
        st.header("🛒 Nueva Venta")
        
        modo = st.radio("Cargar producto:", ["De la Lista", "A mano"], horizontal=True)
        c1, c2 = st.columns([3, 1])
        
        with c1:
            if modo == "A mano":
                p_nom = st.text_input("¿Qué es?", placeholder="Ej: Coca 1.5", key="m_nom")
                p_pre = st.number_input("Precio ($):", min_value=0, step=10, key="m_pre")
            else:
                prods_nombres = [p['nombre'] for p in datos.get('productos', [])]
                sel = st.selectbox("Elegir:", ["Seleccionar..."] + prods_nombres)
                if sel != "Seleccionar...":
                    p_nom = sel
                    p_info = next(i for i in datos['productos'] if i['nombre'] == sel)
                    try: sug = int(float(str(p_info.get('venta', 0)).replace(',','.')))
                    except: sug = 0
                    p_pre = st.number_input("Precio ($):", value=sug, key="f_pre")
                    st.caption(f"Stock actual: {p_info.get('stock', 0)}")
                else:
                    p_nom, p_pre = "", 0

        with c2:
            st.write("##")
            if st.button("➕", help="Sumar otro"):
                if p_nom:
                    st.session_state['items_venta'].append({"nombre": p_nom, "precio": p_pre})
                    st.toast(f"Sumado: {p_nom}")
                else: st.error("Falta info")

        # Mostrar lista acumulada
        if st.session_state['items_venta']:
            st.write("---")
            total_v = 0
            for idx, item in enumerate(st.session_state['items_venta']):
                ca, cb = st.columns([4, 1])
                ca.write(f"✅ {item['nombre']} - ${item['precio']}")
                total_v += item['precio']
                if cb.button("🗑️", key=f"del_{idx}"):
                    st.session_state['items_venta'].pop(idx)
                    st.rerun()
            
            st.write(f"### TOTAL: ${total_v}")
            
            met = st.radio("FORMA DE PAGO:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
            cli = st.selectbox("¿A QUIÉN?", [c['nombre'] for c in datos.get('clientes', [])]) if met == "Fiado" else ""
            
            # Opción de Envío
            es_envio = st.checkbox("🛵 ¿Es para envío?")
            dire = st.text_input("Dirección de entrega:") if es_envio else ""

            if st.button("🚀 FINALIZAR VENTA", use_container_width=True):
                nombres_final = ", ".join([x['nombre'] for x in st.session_state['items_venta']])
                payload = {
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario": st.session_state['usuario'],
                    "monto": total_v,
                    "detalle": f"[{met}] {nombres_final}",
                    "producto_nombre": nombres_final,
                    "metodo": met,
                    "cliente": cli
                }
                if enviar_datos(payload):
                    if es_envio: # Si es envío, mandamos el segundo registro
                        enviar_datos({"tipo": "envio", "cliente": cli if cli else "Mostrador", "direccion": dire, "total": total_v})
                    st.success("Venta guardada!")
                    st.session_state['items_venta'] = []
                    st.rerun()

    # --- SECCIÓN CLIENTES ---
    elif menu == "👥 Clientes":
        st.header("👥 Cuentas de Clientes")
        for c in datos.get('clientes', []):
            saldo = float(c.get('saldo', 0))
            if saldo > 0:
                with st.expander(f"🔴 {c['nombre']} - Debe: ${saldo}"):
                    pago = st.number_input("Monto que paga:", max_value=int(saldo), key=f"p_{c['nombre']}")
                    if st.button("Registrar Cobro", key=f"b_{c['nombre']}"):
                        if enviar_datos({"tipo": "cobro", "cliente": c['nombre'], "monto": pago}):
                            st.rerun()

    # --- SECCIÓN REPARTOS ---
    elif menu == "🛵 Repartos":
        st.header("🛵 Envíos Pendientes")
        envios = datos.get('envios', [])
        if not envios: st.info("No hay repartos pendientes")
        for e in envios:
            st.warning(f"📍 {e['direccion']}\n\n**{e['cliente']}** - ${e['total']}")
            if st.button(f"Marcar Entregado ✅", key=f"env_{e['id']}"):
                if enviar_datos({"tipo": "estado_envio", "id": e['id']}):
                    st.rerun()

    # --- SECCIÓN BALANCE ---
    elif menu == "📊 Balance":
        st.header("📊 Balance de Hoy")
        bal = datos.get('balance', {})
        st.metric("VENTAS TOTALES", f"${bal.get('ventasHoy', 0)}")
        
        c1, c2 = st.columns(2)
        c1.metric("Efectivo", f"${bal.get('efectivo', 0)}")
        c2.metric("M. Pago", f"${bal.get('mercadoPago', 0)}")
        st.metric("Fiados hoy", f"${bal.get('fiados', 0)}")
