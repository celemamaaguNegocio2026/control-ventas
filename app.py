import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión MASTER Pro", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS VISUALES ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #eee; }
    .stButton>button { border-radius: 10px; height: 3em; }
    .card { background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #25D366; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

URL_SCRIPT = "TU_URL_AQUI" # Asegurate de poner tu URL real

def obtener_datos():
    if 'backup_datos' not in st.session_state:
        st.session_state['backup_datos'] = {"productos": [], "clientes": [], "envios": [], "balance": {"ventasHoy": 0, "efectivo": 0, "mercadoPago": 0, "fiados": 0}, "historial": [], "topVentas": {}}
    try:
        r = requests.get(URL_SCRIPT, timeout=12)
        if r.status_code == 200:
            st.session_state['backup_datos'] = r.json()
            return r.json()
        return st.session_state['backup_datos']
    except: return st.session_state['backup_datos']

def enviar_datos(payload):
    try: return requests.post(URL_SCRIPT, params=payload, timeout=12).status_code == 200
    except: return False

# --- GESTIÓN DE ACCESO ---
usuarios = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso al Sistema")
    u = st.selectbox("Elegí tu nombre:", ["Seleccionar..."] + list(usuarios.keys()))
    p = st.text_input("PIN de acceso:", type="password")
    if st.button("INGRESAR", key="btn_login"):
        if p == usuarios.get(u):
            st.session_state.update({"autenticado": True, "usuario": u}); st.rerun()
        else: st.error("PIN Incorrecto")
else:
    # --- MENÚ HAMBURGUESA (SIDEBAR) ---
    with st.sidebar:
        st.header(f"✨ Hola {st.session_state['usuario']}")
        st.divider()
        # Radio para navegación
        menu = st.selectbox(
            "IR A:",
            ["💰 Nueva Venta", "👥 Clientes / Deudas", "🛵 Repartos", "🔍 Radar Ofertas", "📊 Balance Diario"],
            index=0,
            key="menu_principal"
        )
        st.divider()
        # El botón de cerrar sesión ahora tiene una KEY única para evitar el error
        if st.button("🚪 Cerrar Sesión", key="btn_logout_sidebar"):
            st.session_state['autenticado'] = False; st.rerun()

    # --- CARGA DE DATOS ---
    d = obtener_datos()
    prods, clis, envios, bal, historial, top = d.get('productos', []), d.get('clientes', []), d.get('envios', []), d.get('balance', {}), d.get('historial', []), d.get('topVentas', {})

    # --- LÓGICA DE NAVEGACIÓN ---
    
    if menu == "💰 Nueva Venta":
        st.header("🛒 Registrar Venta")
        col1, col2 = st.columns([2,1])
        with col1:
            n_prods = [p['nombre'] for p in prods]
            sel = st.selectbox("¿Qué vendiste?", ["Venta Manual"] + n_prods, key="sel_producto")
            if sel != "Venta Manual":
                p_info = next(i for i in prods if i['nombre'] == sel)
                try: precio = int(float(str(p_info.get('venta', 0)).replace(',','.')))
                except: precio = 0
                monto = st.number_input("Precio:", value=precio, key="monto_p")
                st.caption(f"Stock actual: {p_info.get('stock', 0)}")
                det, p_nom = f"Venta: {sel}", sel
            else:
                monto = st.number_input("Monto:", min_value=0, key="monto_manual")
                det = st.text_input("Detalle de la venta:", key="det_manual")
                p_nom = ""
        with col2:
            met = st.radio("Forma de Pago:", ["Efectivo", "Mercado Pago", "Fiado"], key="radio_pago")
            cli = st.selectbox("Elegir Cliente:", [c['nombre'] for c in clis], key="sel_cliente_fiado") if met == "Fiado" else ""
            env = st.checkbox("¿Necesita Envío?", key="check_envio")
            dir_e = st.text_input("Dirección:", key="input_dir") if env else ""

        if st.button("🚀 GUARDAR OPERACIÓN", key="btn_guardar_venta"):
            payload = {"fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "usuario": st.session_state['usuario'], "monto": monto, "detalle": f"[{met}] {det}", "producto_nombre": p_nom, "metodo": met, "cliente": cli}
            if enviar_datos(payload):
                if env: enviar_datos({"tipo": "envio", "cliente": cli if cli else "Mostrador", "direccion": dir_e, "total": monto})
                st.success("¡Venta guardada con éxito!"); st.rerun()

    elif menu == "👥 Clientes / Deudas":
        st.header("👥 Gestión de Deudores")
        for c in clis:
            saldo = float(c.get('saldo', 0))
            if saldo > 0:
                with st.expander(f"👤 {c['nombre']} | Debe: ${saldo}"):
                    pago = st.number_input(f"Anotar entrega para {c['nombre']}", max_value=int(saldo), key=f"pago_{c['nombre']}")
                    if st.button(f"Cobrar ${pago}", key=f"btn_cobro_{c['nombre']}"):
                        if enviar_datos({"tipo": "cobro", "cliente": c['nombre'], "monto": pago}): st.rerun()

    elif menu == "🛵 Repartos":
        st.header("🛵 Envíos por Entregar")
        if not envios: st.info("No hay pedidos pendientes.")
        for e in envios:
            st.markdown(f"""<div class="card">
                <b>Cliente:</b> {e['cliente']}<br>
                <b>A Cobrar:</b> ${e['total']}<br>
                📍 {e['direccion']}
                </div>""", unsafe_allow_html=True)
            if st.button(f"Entregado ✅", key=f"btn_env_{e['id']}"):
                if enviar_datos({"tipo": "estado_envio", "id": e['id']}): st.rerun()

    elif menu == "🔍 Radar Ofertas":
        st.header("🔍 Radar de Clientes")
        st.write("Buscá quién compró un producto para avisarle de una oferta.")
        it = st.text_input("Producto:", key="input_radar")
        if it:
            interesados = list(set([h['cliente'] for h in historial if it.lower() in str(h['detalle']).lower() and h['cliente'] != ""]))
            if interesados:
                for cli_n in interesados: st.write(f"✅ {cli_n}")
            else: st.info("No hay clientes registrados con ese producto.")

    elif menu == "📊 Balance Diario":
        st.header("📊 Resumen de la Jornada")
        v_total = bal.get('ventasHoy', 0)
        
        st.write("**Meta del día ($30.000)**")
        st.progress(min(v_total / 30000, 1.0))

        c1, c2, c3 = st.columns(3)
        c1.metric("💵 Efec", f"${bal.get('efectivo', 0)}")
        c2.metric("💳 MP", f"${bal.get('mercadoPago', 0)}")
        c3.metric("📝 Fiado", f"${bal.get('fiados', 0)}")

        st.divider()
        reporte = f"*CIERRE* %0A💰 Total: ${v_total}%0A💵 Efec: ${bal.get('efectivo',0)}%0A💳 MP: ${bal.get('mercadoPago',0)}%0A👤: {st.session_state['usuario']}"
        st.markdown(f'<a href="https://wa.me/?text={reporte}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">📤 ENVIAR CIERRE A WHATSAPP</button></a>', unsafe_allow_html=True)
