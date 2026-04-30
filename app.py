import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión MASTER Pro", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS VISUALES (Simplificados para evitar bloqueos en móvil) ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 10px; border-radius: 8px; border: 1px solid #ddd; }
    .stButton>button { border-radius: 8px; height: 3.5em; width: 100%; font-weight: bold; }
    /* Estilo para que los inputs se vean mejor en móvil */
    .stTextInput input, .stNumberInput input { font-size: 16px !important; } 
    </style>
    """, unsafe_allow_html=True)

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

# --- FUNCIONES DE DATOS ---
def obtener_datos():
    if 'backup_datos' not in st.session_state:
        st.session_state['backup_datos'] = {
            "productos": [], "clientes": [], "envios": [], 
            "balance": {"ventasHoy": 0, "efectivo": 0, "mercadoPago": 0, "fiados": 0},
            "historial": [], "topVentas": {}
        }
    try:
        r = requests.get(URL_SCRIPT, timeout=10)
        if r.status_code == 200:
            st.session_state['backup_datos'] = r.json()
            return r.json()
        return st.session_state['backup_datos']
    except:
        return st.session_state['backup_datos']

def enviar_datos(payload):
    try:
        r = requests.post(URL_SCRIPT, params=payload, timeout=10)
        return r.status_code == 200
    except: return False

# --- GESTIÓN DE ACCESO ---
usuarios = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
if 'autenticado' not in st.session_state: 
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso")
    u = st.selectbox("Usuario:", ["Seleccionar..."] + list(usuarios.keys()), key="l_user")
    p = st.text_input("PIN:", type="password", key="l_pin")
    if st.button("INGRESAR", key="l_btn"):
        if p == usuarios.get(u):
            st.session_state.update({"autenticado": True, "usuario": u})
            st.rerun()
        else: st.error("PIN Incorrecto")
else:
    d = obtener_datos()
    prods = d.get('productos', [])
    clis = d.get('clientes', [])
    envios = d.get('envios', [])
    bal = d.get('balance', {})
    historial = d.get('historial', [])

    # --- SIDEBAR (Menú Hamburguesa) ---
    with st.sidebar:
        st.header(f"Hola {st.session_state['usuario']}")
        menu = st.radio("MENÚ", ["💰 Ventas", "👥 Clientes", "🛵 Repartos", "📊 Balance"], key="nav")
        if st.button("Cerrar Sesión", key="logout"):
            st.session_state['autenticado'] = False
            st.rerun()

    # --- SECCIÓN VENTAS ---
    if menu == "💰 Ventas":
        st.subheader("Registrar Venta")
        
        n_prods = [p['nombre'] for p in prods]
        sel = st.selectbox("Producto:", ["Escribir manual..."] + n_prods, key="s_prod")
        
        if sel == "Escribir manual...":
            p_nom = st.text_input("¿Qué vendiste?", key="input_manual_nombre")
            monto = st.number_input("Precio ($):", min_value=0, key="input_manual_precio")
            det_v = f"Manual: {p_nom}"
        else:
            p_info = next(i for i in prods if i['nombre'] == sel)
            try: precio_sug = int(float(str(p_info.get('venta', 0)).replace(',','.')))
            except: precio_sug = 0
            p_nom = sel
            monto = st.number_input("Precio:", value=precio_sug, key="input_fix_precio")
            st.caption(f"Stock: {p_info.get('stock', 0)}")
            det_v = f"Venta: {sel}"

        met = st.radio("Pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True, key="s_pago")
        cli = st.selectbox("¿A quién?", [c['nombre'] for c in clis], key="s_cli") if met == "Fiado" else ""
        
        env_c = st.checkbox("🛵 ¿Es para envío?", key="c_env")
        dir_e = st.text_input("Dirección:", key="i_dir") if env_c else ""

        if st.button("🚀 GUARDAR VENTA", key="g_venta"):
            if not p_nom:
                st.error("Escribí el nombre del producto")
            else:
                payload = {
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario": st.session_state['usuario'],
                    "monto": monto,
                    "detalle": f"[{met}] {det_v}",
                    "producto_nombre": p_nom,
                    "metodo": met,
                    "cliente": cli
                }
                if enviar_datos(payload):
                    if env_c: enviar_datos({"tipo": "envio", "cliente": cli if cli else "Mostrador", "direccion": dir_e, "total": monto})
                    st.success("Guardado!"); st.rerun()

    # --- SECCIÓN CLIENTES ---
    elif menu == "👥 Clientes":
        st.subheader("Deudas")
        for c in clis:
            saldo = float(c.get('saldo', 0))
            if saldo > 0:
                with st.expander(f"{c['nombre']} - ${saldo}"):
                    pago = st.number_input("Cobrar:", max_value=int(saldo), key=f"p_{c['nombre']}")
                    if st.button("Cobrar ahora", key=f"b_{c['nombre']}"):
                        if enviar_datos({"tipo": "cobro", "cliente": c['nombre'], "monto": pago}): st.rerun()

    # --- SECCIÓN REPARTOS ---
    elif menu == "🛵 Repartos":
        st.subheader("Pedidos")
        for e in envios:
            st.info(f"**{e['cliente']}** - ${e['total']}\n\n📍 {e['direccion']}")
            if st.button(f"Entregado ✅", key=f"e_{e['id']}"):
                if enviar_datos({"tipo": "estado_envio", "id": e['id']}): st.rerun()

    # --- SECCIÓN BALANCE ---
    elif menu == "📊 Balance":
        st.subheader("Resumen de hoy")
        st.metric("Total Hoy", f"${bal.get('ventasHoy', 0)}")
        c1, c2 = st.columns(2)
        c1.metric("Efectivo", f"${bal.get('efectivo', 0)}")
        c2.metric("M. Pago", f"${bal.get('mercadoPago', 0)}")
        
        if st.button("Mandar reporte por WhatsApp"):
            reporte = f"CIERRE: Total ${bal.get('ventasHoy', 0)}"
            st.markdown(f'<a href="https://wa.me/?text={reporte}" target="_blank">Abrir WhatsApp</a>', unsafe_allow_html=True)
