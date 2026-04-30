import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión MASTER", layout="centered", initial_sidebar_state="expanded")

# CSS para forzar que los inputs sean clickeables en móvil
st.markdown("""
    <style>
    input { font-size: 16px !important; }
    .stTextInput>div>div>input { pointer-events: auto !important; }
    </style>
    """, unsafe_allow_html=True)

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

def obtener_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=10)
        return r.json()
    except:
        return st.session_state.get('backup', {"productos":[], "clientes":[], "balance":{}, "envios":[], "historial":[]})

def enviar_datos(payload):
    try:
        return requests.post(URL_SCRIPT, params=payload, timeout=10).status_code == 200
    except: return False

if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False

# --- LOGIN ---
if not st.session_state['autenticado']:
    st.title("🔐 Acceso")
    u = st.selectbox("Usuario:", ["Seleccionar...", "Celeste", "Agu", "Mamá"], key="user_sel")
    p = st.text_input("PIN:", type="password", key="pin_sel")
    if st.button("INGRESAR"):
        pins = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
        if p == pins.get(u):
            st.session_state.update({"autenticado": True, "usuario": u})
            st.rerun()
        else: st.error("PIN incorrecto")

# --- APP CON MENU HAMBURGUESA ---
else:
    datos = obtener_datos()
    st.session_state['backup'] = datos

    # MENU LATERAL
    with st.sidebar:
        st.title(f"👋 Hola {st.session_state['usuario']}")
        menu = st.radio("MENÚ", ["💰 Ventas", "👥 Clientes", "🛵 Repartos", "📊 Balance"], key="nav_menu")
        st.divider()
        if st.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()

    # --- SECCIÓN VENTAS ---
    if menu == "💰 Ventas":
        st.header("🛒 Nueva Venta")
        
        prods = [p['nombre'] for p in datos.get('productos', [])]
        
        # Primero preguntamos qué quiere hacer
        modo = st.radio("¿Qué vas a cargar?", ["Producto de la lista", "Escribir nombre a mano"], horizontal=True)
        
        if modo == "Escribir nombre a mano":
            # Campo de texto puro para que el celular abra el teclado
            p_nom = st.text_input("ESCRIBÍ EL PRODUCTO AQUÍ:", placeholder="Ej: Sprite 2.25L", key="txt_manual")
            monto = st.number_input("PRECIO ($):", min_value=0, step=10, key="num_manual")
            detalle_final = f"Manual: {p_nom}"
        else:
            sel = st.selectbox("ELEGIR PRODUCTO:", ["Seleccionar..."] + prods, key="sel_lista")
            if sel != "Seleccionar...":
                p_info = next(i for i in datos['productos'] if i['nombre'] == sel)
                p_nom = sel
                try: sugerido = int(float(str(p_info.get('venta', 0)).replace(',','.')))
                except: sugerido = 0
                monto = st.number_input("PRECIO ($):", value=sugerido, key="num_lista")
                st.info(f"Stock: {p_info.get('stock', 0)}")
                detalle_final = f"Venta: {sel}"
            else:
                p_nom = ""

        st.divider()
        met = st.radio("FORMA DE PAGO:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
        
        cli = ""
        if met == "Fiado":
            cli = st.selectbox("¿QUIÉN DEBE?:", [c['nombre'] for c in datos.get('clientes', [])])

        if st.button("🚀 GUARDAR VENTA"):
            if not p_nom:
                st.error("Por favor, poné un nombre al producto")
            else:
                payload = {
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario": st.session_state['usuario'],
                    "monto": monto,
                    "detalle": f"[{met}] {detalle_final}",
                    "producto_nombre": p_nom,
                    "metodo": met,
                    "cliente": cli
                }
                if enviar_datos(payload):
                    st.success("¡Venta guardada!")
                    st.rerun()

    # --- SECCIÓN CLIENTES ---
    elif menu == "👥 Clientes":
        st.header("👥 Cuentas")
        for c in datos.get('clientes', []):
            saldo = float(c.get('saldo', 0))
            if saldo > 0:
                with st.expander(f"🔴 {c['nombre']} - Debe: ${saldo}"):
                    pago = st.number_input(f"Anotar pago de {c['nombre']}", max_value=int(saldo), key=f"p_{c['nombre']}")
                    if st.button("Cobrar", key=f"b_{c['nombre']}"):
                        if enviar_datos({"tipo": "cobro", "cliente": c['nombre'], "monto": pago}): st.rerun()

    # --- SECCIÓN REPARTOS ---
    elif menu == "🛵 Repartos":
        st.header("🛵 Envíos")
        envios = datos.get('envios', [])
        if not envios: st.write("No hay pendientes.")
        for e in envios:
            st.info(f"**{e['cliente']}**\n{e['direccion']}\nTotal: ${e['total']}")
            if st.button(f"Entregado ✅", key=f"env_{e['id']}"):
                enviar_datos({"tipo": "estado_envio", "id": e['id']})
                st.rerun()

    # --- SECCIÓN BALANCE ---
    elif menu == "📊 Balance":
        st.header("📊 Resumen")
        bal = datos.get('balance', {})
        st.metric("TOTAL HOY", f"${bal.get('ventasHoy', 0)}")
        st.write(f"💵 Efectivo: ${bal.get('efectivo', 0)}")
        st.write(f"💳 M.Pago: ${bal.get('mercadoPago', 0)}")
        st.write(f"📝 Fiado: ${bal.get('fiados', 0)}")
