import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Familiar MASTER Pro", layout="wide")
# REEMPLAZÁ CON TU URL REAL DE APPS SCRIPT
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

def obtener_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=15)
        if r.status_code == 200:
            return r.json()
        return {}
    except: return {}

def enviar_datos(payload):
    try:
        r = requests.post(URL_SCRIPT, params=payload, timeout=15)
        return r.status_code == 200
    except: return False

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
            else: st.error("PIN Incorrecto")
else:
    # --- CARGA DE DATOS ---
    with st.spinner("Sincronizando..."):
        d = obtener_datos()
        prods = d.get('productos', [])
        clis = d.get('clientes', [])
        envios = d.get('envios', [])
        bal = d.get('balance', {})
        historial = d.get('historial', [])

    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    tabs = st.tabs(["💰 VENTAS", "👥 CLIENTES", "🛵 REPARTO", "🔍 INTELIGENCIA", "📊 BALANCE"])

    # --- TAB 1: VENTAS ---
    with tabs[0]:
        st.subheader("Registrar Venta")
        nombres_p = [p['nombre'] for p in prods]
        sel_p = st.selectbox("Producto:", ["Manual"] + nombres_p)
        
        if sel_p != "Manual":
            p_data = next(item for item in prods if item['nombre'] == sel_p)
            try:
                precio_sug = int(float(str(p_data.get('venta', '0')).replace(',', '.')))
            except: precio_sug = 0
            monto = st.number_input("Precio ($):", value=precio_sug)
            st.caption(f"Stock: {p_data.get('stock', 0)}")
            desc = f"Venta: {sel_p}"
            p_nombre = sel_p
        else:
            monto = st.number_input("Monto ($):", min_value=0)
            desc = st.text_input("Detalle:")
            p_nombre = ""

        metodo = st.radio("Pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
        c_fiado = st.selectbox("¿A quién?", [c['nombre'] for c in clis]) if metodo == "Fiado" else ""
        
        if st.button("🚀 GUARDAR"):
            payload = {
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "usuario": st.session_state['usuario'],
                "monto": monto,
                "detalle": f"[{metodo}] {desc}",
                "producto_nombre": p_nombre,
                "metodo": metodo,
                "cliente": c_fiado
            }
            if enviar_datos(payload):
                st.success("¡Venta Guardada!"); st.rerun()

    # --- TAB 2: CLIENTES ---
    with tabs[1]:
        st.subheader("Cuentas Fiadas")
        for c in clis:
            saldo = float(c.get('saldo', 0))
            if saldo > 0:
                with st.expander(f"🔴 {c['nombre']} - Debe: ${saldo}"):
                    pago = st.number_input(f"Paga {c['nombre']}", min_value=0, max_value=int(saldo), key=f"p_{c['nombre']}")
                    if st.button(f"Cobrar", key=f"b_{c['nombre']}"):
                        if enviar_datos({"tipo": "cobro", "cliente": c['nombre'], "monto": pago}): st.rerun()

    # --- TAB 3: REPARTO ---
    with tabs[2]:
        st.subheader("Envíos Pendientes")
        for e in envios:
            with st.container(border=True):
                st.write(f"**{e['cliente']}** - ${e['total']}")
                st.write(f"🏠 {e['direccion']}")
                if st.button("Entregado", key=f"env_{e['id']}"):
                    if enviar_datos({"tipo": "estado_envio", "id": e['id']}): st.rerun()

    # --- TAB 4: INTELIGENCIA ---
    with tabs[3]:
        st.subheader("Buscador de Clientes")
        it = st.text_input("Producto:")
        if it:
            interesados = list(set([h['cliente'] for h in historial if it.lower() in h['detalle'].lower() and h['cliente'] != ""]))
            for cli in interesados:
                st.write(f"👤 {cli}")

    # --- TAB 5: BALANCE ---
    with tabs[4]:
        st.header("Cierre del Día")
        v_tot = bal.get('ventasHoy', 0)
        efectivo = bal.get('efectivo', 0)
        mp = bal.get('mercadoPago', 0)
        fiados = bal.get('fiados', 0)

        c1, c2, c3 = st.columns(3)
        c1.metric("💵 Efectivo", f"${efectivo}")
        c2.metric("💳 Mercado Pago", f"${mp}")
        c3.metric("📝 Fiados", f"${fiados}")

        st.divider()

        # Reporte WhatsApp
        reporte = (
            f"*CIERRE DE HOY - {datetime.now().strftime('%d/%m/%Y')}*%0A"
            f"💰 *Total:* ${v_tot}%0A"
            f"💵 *Efectivo:* ${efectivo}%0A"
            f"💳 *MP:* ${mp}%0A"
            f"📝 *Fiados:* ${fiados}%0A"
            f"👤 *Hizo el cierre:* {st.session_state['usuario']}"
        )
        
        st.markdown(f"""
            <a href="https://wa.me/?text={reporte}" target="_blank">
                <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">
                    📤 ENVIAR CIERRE POR WHATSAPP
                </button>
            </a>
        """, unsafe_allow_html=True)

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False; st.rerun()
