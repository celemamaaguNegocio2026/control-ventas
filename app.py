import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN BÁSICA ---
st.set_page_config(page_title="Gestión MASTER", layout="centered", initial_sidebar_state="collapsed")

# URL DE TU SCRIPT (Mantenela siempre igual)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

# --- FUNCIONES DE DATOS ---
def obtener_datos():
    if 'backup_datos' not in st.session_state:
        st.session_state['backup_datos'] = {"productos": [], "clientes": [], "envios": [], "balance": {"ventasHoy": 0, "efectivo": 0, "mercadoPago": 0, "fiados": 0}}
    try:
        r = requests.get(URL_SCRIPT, timeout=10)
        if r.status_code == 200:
            st.session_state['backup_datos'] = r.json()
            return r.json()
        return st.session_state['backup_datos']
    except: return st.session_state['backup_datos']

def enviar_datos(payload):
    try:
        r = requests.post(URL_SCRIPT, params=payload, timeout=10)
        return r.status_code == 200
    except: return False

# --- LOGIN SIMPLE ---
usuarios = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.header("🔐 Acceso")
    u = st.selectbox("Usuario:", ["Seleccionar..."] + list(usuarios.keys()), key="login_u")
    p = st.text_input("PIN:", type="password", key="login_p")
    if st.button("INGRESAR", key="login_b"):
        if p == usuarios.get(u):
            st.session_state.update({"autenticado": True, "usuario": u})
            st.rerun()
        else: st.error("Incorrecto")
else:
    # CARGA DE DATOS
    d = obtener_datos()
    prods = d.get('productos', [])
    clis = d.get('clientes', [])
    bal = d.get('balance', {})

    # --- MENÚ LATERAL (HAMBURGUESA) ---
    with st.sidebar:
        st.write(f"👤 {st.session_state['usuario']}")
        menu = st.radio("IR A:", ["VENTAS", "CLIENTES", "BALANCE"], key="main_menu")
        if st.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()

    # --- SECCIÓN VENTAS ---
    if menu == "VENTAS":
        st.subheader("🛒 Nueva Venta")
        
        # PRODUCTO
        n_prods = [p['nombre'] for p in prods]
        sel = st.selectbox("Elegir producto:", ["ESCRIBIR NOMBRE..."] + n_prods, key="s_v")
        
        if sel == "ESCRIBIR NOMBRE...":
            # Usamos label visible y simple para que el celular lo detecte
            p_nom = st.text_input("NOMBRE DEL PRODUCTO:", key="v_manual_nom")
            monto = st.number_input("PRECIO ($):", min_value=0, step=1, key="v_manual_pre")
            det_final = f"Manual: {p_nom}"
        else:
            p_info = next(i for i in prods if i['nombre'] == sel)
            try: pre_sug = int(float(str(p_info.get('venta', 0)).replace(',','.')))
            except: pre_sug = 0
            p_nom = sel
            monto = st.number_input("PRECIO ($):", value=pre_sug, key="v_fix_pre")
            st.write(f"Stock: {p_info.get('stock', 0)}")
            det_final = f"Venta: {sel}"

        st.divider()
        
        # PAGO
        met = st.radio("PAGO CON:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True, key="v_met")
        cli = st.selectbox("CLIENTE (Si es fiado):", [c['nombre'] for c in clis], key="v_cli") if met == "Fiado" else ""
        
        st.divider()

        if st.button("✅ GUARDAR VENTA", key="v_save"):
            if sel == "ESCRIBIR NOMBRE..." and not p_nom:
                st.error("Falta el nombre")
            else:
                payload = {
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario": st.session_state['usuario'],
                    "monto": monto,
                    "detalle": f"[{met}] {det_final}",
                    "producto_nombre": p_nom,
                    "metodo": met,
                    "cliente": cli
                }
                if enviar_datos(payload):
                    st.success("¡Venta cargada!")
                    st.rerun()

    # --- SECCIÓN BALANCE ---
    elif menu == "BALANCE":
        st.subheader("📊 Balance de Hoy")
        st.metric("Total", f"${bal.get('ventasHoy', 0)}")
        st.write(f"Efectivo: ${bal.get('efectivo', 0)}")
        st.write(f"M. Pago: ${bal.get('mercadoPago', 0)}")
