import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión MASTER Pro", layout="wide", initial_sidebar_state="collapsed")

# --- ESTILOS VISUALES (CSS) ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #eee; }
    .stButton>button { border-radius: 10px; height: 3em; width: 100%; }
    .card { background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #25D366; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    [data-testid="stSidebarNav"] { background-image: none; }
    </style>
    """, unsafe_allow_html=True)

# URL DE TU APPS SCRIPT (Asegúrate que sea la correcta)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

# --- PROTECCIÓN DE DATOS (BACKUP INTERNO) ---
def obtener_datos():
    if 'backup_datos' not in st.session_state:
        st.session_state['backup_datos'] = {
            "productos": [], "clientes": [], "envios": [], 
            "balance": {"ventasHoy": 0, "efectivo": 0, "mercadoPago": 0, "fiados": 0},
            "historial": [], "topVentas": {}
        }
    try:
        r = requests.get(URL_SCRIPT, timeout=12)
        if r.status_code == 200:
            nuevos_datos = r.json()
            if nuevos_datos and "productos" in nuevos_datos:
                st.session_state['backup_datos'] = nuevos_datos
                return nuevos_datos
        st.warning("⚠️ Usando copia de seguridad (Problema de conexión con Excel)")
        return st.session_state['backup_datos']
    except:
        return st.session_state['backup_datos']

def enviar_datos(payload):
    try:
        r = requests.post(URL_SCRIPT, params=payload, timeout=12)
        return r.status_code == 200
    except: return False

# --- GESTIÓN DE ACCESO ---
usuarios = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
if 'autenticado' not in st.session_state: 
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso al Sistema")
    u = st.selectbox("Elegí tu nombre:", ["Seleccionar..."] + list(usuarios.keys()), key="login_user")
    p = st.text_input("PIN de acceso:", type="password", key="login_pin")
    if st.button("INGRESAR", key="btn_login"):
        if p == usuarios.get(u):
            st.session_state.update({"autenticado": True, "usuario": u})
            st.rerun()
        else: st.error("PIN Incorrecto")
else:
    # --- CARGA INICIAL DE DATOS ---
    d = obtener_datos()
    prods = d.get('productos', [])
    clis = d.get('clientes', [])
    envios = d.get('envios', [])
    bal = d.get('balance', {})
    historial = d.get('historial', [])
    top = d.get('topVentas', {})

    # --- MENÚ HAMBURGUESA (SIDEBAR) ---
    with st.sidebar:
        st.header(f"✨ Hola {st.session_state['usuario']}")
        st.divider()
        menu = st.radio(
            "MENÚ PRINCIPAL",
            ["💰 Nueva Venta", "👥 Clientes / Deudas", "🛵 Repartos", "🔍 Radar Ofertas", "📊 Balance Diario"],
            key="menu_navegacion"
        )
        st.divider()
        if st.button("🚪 Cerrar Sesión", key="btn_logout"):
            st.session_state['autenticado'] = False
            st.rerun()

    # --- 1. SECCIÓN VENTAS (FLEXIBLE) ---
    if menu == "💰 Nueva Venta":
        st.header("🛒 Registrar Venta")
        col1, col2 = st.columns([2,1])
        
        with col1:
            n_prods = [p['nombre'] for p in prods]
            opciones = ["Escribir nombre manualmente..."] + n_prods
            sel = st.selectbox("Producto:", opciones, key="sel_producto")
            
            if sel == "Escribir nombre manualmente...":
                p_nom = st.text_input("Nombre del producto:", placeholder="Ej: Sprite 2.25L", key="p_nombre_manual")
                monto = st.number_input("Precio ($):", min_value=0, key="monto_manual")
                det = f"Venta Manual: {p_nom}"
            else:
                p_info = next(i for i in prods if i['nombre'] == sel)
                try: precio_sug = int(float(str(p_info.get('venta', 0)).replace(',','.')))
                except: precio_sug = 0
                p_nom = sel
                monto = st.number_input("Confirmar Precio ($):", value=precio_sug, key="monto_p")
                stock = p_info.get('stock', 0)
                if stock <= 3: st.error(f"🚨 ¡STOCK CRÍTICO! Quedan {stock}")
                else: st.info(f"📦 Stock disponible: {stock}")
                det = f"Venta: {sel}"

        with col2:
            met = st.radio("Forma de Pago:", ["Efectivo", "Mercado Pago", "Fiado"], key="radio_pago")
            cli = st.selectbox("¿A quién?", [c['nombre'] for c in clis], key="sel_cli_fiado") if met == "Fiado" else ""
            env_check = st.checkbox("🛵 ¿Es con envío?", key="check_envio")
            dir_e = st.text_input("Dirección de entrega:", key="input_dir") if env_check else ""

        if st.button("🚀 REGISTRAR VENTA FINAL", key="btn_guardar_venta"):
            if not p_nom:
                st.error("Por favor, escribí un nombre para el producto.")
            else:
                payload = {
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario": st.session_state['usuario'],
                    "monto": monto,
                    "detalle": f"[{metodo if 'metodo' in locals() else met}] {det}",
                    "producto_nombre": p_nom,
                    "metodo": met,
                    "cliente": cli
                }
                if enviar_datos(payload):
                    if env_check:
                        enviar_datos({"tipo": "envio", "cliente": cli if cli else "Mostrador", "direccion": dir_e, "total": monto})
                    st.balloons()
                    st.success("¡Venta Guardada!"); st.rerun()

    # --- 2. SECCIÓN CLIENTES ---
    elif menu == "👥 Clientes / Deudas":
        st.header("👥 Cuentas de Clientes")
        for c in clis:
            saldo = float(c.get('saldo', 0))
            if saldo > 0:
                with st.expander(f"🔴 {c['nombre']} - Debe: ${saldo}"):
                    pago = st.number_input(f"Anotar entrega para {c['nombre']}", max_value=int(saldo), key=f"pago_{c['nombre']}")
                    if st.button(f"Cobrar", key=f"btn_cobro_{c['nombre']}"):
                        if enviar_datos({"tipo": "cobro", "cliente": c['nombre'], "monto": pago}): st.rerun()
            else: st.write(f"🟢 {c['nombre']} (Al día)")

    # --- 3. SECCIÓN REPARTOS ---
    elif menu == "🛵 Repartos":
        st.header("🛵 Pedidos Pendientes")
        if not envios: st.info("No hay envíos por entregar.")
        for e in envios:
            st.markdown(f"""<div class="card">
                <b>{e['cliente']}</b><br>Cobrar: ${e['total']}<br>🏠 {e['direccion']}
                </div>""", unsafe_allow_html=True)
            if st.button(f"Entregado ✅", key=f"btn_env_{e['id']}"):
                if enviar_datos({"tipo": "estado_envio", "id": e['id']}): st.rerun()

    # --- 4. SECCIÓN RADAR ---
    elif menu == "🔍 Radar Ofertas":
        st.header("🔍 Radar de Clientes")
        it = st.text_input("Buscar quién compró:", placeholder="Ej: Coca", key="input_radar")
        if it:
            interesados = list(set([h['cliente'] for h in historial if it.lower() in str(h['detalle']).lower() and h['cliente'] != ""]))
            for cli_n in interesados:
                col_r1, col_r2 = st.columns([3, 1])
                col_r1.write(f"👤 {cli_n}")
                c_info = next((item for item in clis if item["nombre"] == cli_n), None)
                if c_info and c_info.get("tel"):
                    tel = str(c_info["tel"]).replace("+", "").replace(" ", "")
                    col_r2.markdown(f"[💬 WhatsApp](https://wa.me/{tel})")

    # --- 5. SECCIÓN BALANCE ---
    elif menu == "📊 Balance Diario":
        st.header("📊 Resumen de hoy")
        v_total = bal.get('ventasHoy', 0)
        st.write(f"**Progreso Meta Diaria ($30.000)**")
        st.progress(min(v_total / 30000, 1.0))

        c1, c2, c3 = st.columns(3)
        c1.metric("💵 Efec", f"${bal.get('efectivo', 0)}")
        c2.metric("💳 MP", f"${bal.get('mercadoPago', 0)}")
        c3.metric("📝 Fiado", f"${bal.get('fiados', 0)}")

        st.divider()
        reporte = (f"*CIERRE {datetime.now().strftime('%d/%m')}*%0A"
                   f"💰 Total: ${v_total}%0A"
                   f"💵 Efec: ${bal.get('efectivo',0)}%0A"
                   f"💳 MP: ${bal.get('mercadoPago',0)}%0A"
                   f"👤 Responsable: {st.session_state['usuario']}")
        
        st.markdown(f'<a href="https://wa.me/?text={reporte}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:10px; font-weight:bold; cursor:pointer;">📤 ENVIAR CIERRE A WHATSAPP</button></a>', unsafe_allow_html=True)
        
        if top:
            st.subheader("🔥 Lo más vendido")
            df_top = pd.DataFrame(top.items(), columns=['Producto', 'Cant']).sort_values(by='Cant', ascending=False)
            st.table(df_top.head(5))
