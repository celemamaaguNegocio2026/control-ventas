import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión MASTER - SISTEMA TOTAL", layout="wide")
# REEMPLAZÁ CON TU URL REAL DE APPS SCRIPT
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

# --- LOGIN ---
usuarios = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso Sistema Familiar")
    u = st.selectbox("Usuario:", ["Seleccionar..."] + list(usuarios.keys()))
    if u != "Seleccionar...":
        p = st.text_input("PIN:", type="password")
        if st.button("ENTRAR"):
            if p == usuarios[u]:
                st.session_state.update({"autenticado": True, "usuario": u}); st.rerun()
            else: st.error("PIN Incorrecto")
else:
    # --- CARGA DE DATOS ---
    with st.spinner("Cargando sistema..."):
        d = obtener_datos()
        prods = d.get('productos', [])
        clis = d.get('clientes', [])
        envios = d.get('envios', [])
        bal = d.get('balance', {})
        historial = d.get('historial', [])
        top = d.get('topVentas', {})

    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    tabs = st.tabs(["💰 VENTAS", "👥 CLIENTES", "🛵 REPARTO", "🔍 INTELIGENCIA", "📊 BALANCE"])

    # --- TAB 1: VENTAS (CON ALERTAS DE STOCK) ---
    with tabs[0]:
        st.subheader("Nueva Venta")
        nombres_p = [p['nombre'] for p in prods]
        sel_p = st.selectbox("Producto:", ["Manual"] + nombres_p)
        
        p_nombre_stock = ""
        if sel_p != "Manual":
            p_data = next(item for item in prods if item['nombre'] == sel_p)
            try: precio_sug = int(float(str(p_data.get('venta', '0')).replace(',', '.')))
            except: precio_sug = 0
            monto = st.number_input("Precio ($):", value=precio_sug)
            stock_actual = p_data.get('stock', 0)
            if stock_actual <= 3: st.error(f"⚠️ ¡STOCK CRÍTICO: {stock_actual}!")
            else: st.info(f"Stock disponible: {stock_actual}")
            desc, p_nombre_stock = f"Venta: {sel_p}", sel_p
        else:
            monto = st.number_input("Monto ($):", min_value=0)
            desc = st.text_input("Detalle de la venta:")
            p_nombre_stock = ""

        metodo = st.radio("Método de Pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
        c_fiado = st.selectbox("Seleccionar Cliente:", [c['nombre'] for c in clis]) if metodo == "Fiado" else ""
        
        es_envio = st.checkbox("¿Es un envío a domicilio?")
        direccion = st.text_input("Dirección de entrega:") if es_envio else ""
        
        if st.button("🚀 REGISTRAR VENTA"):
            payload = {
                "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                "usuario": st.session_state['usuario'],
                "monto": monto,
                "detalle": f"[{metodo}] {desc}",
                "producto_nombre": p_nombre_stock,
                "metodo": metodo,
                "cliente": c_fiado
            }
            if enviar_datos(payload):
                if es_envio:
                    enviar_datos({"tipo": "envio", "fecha": payload["fecha"], "cliente": c_fiado if c_fiado else "Mostrador", "direccion": direccion, "total": monto})
                st.success("¡Venta y Stock actualizados!"); st.rerun()

    # --- TAB 2: CLIENTES (CON COBROS) ---
    with tabs[1]:
        st.subheader("Cuentas Pendientes")
        for c in clis:
            saldo = float(c.get('saldo', 0))
            if saldo > 0:
                with st.expander(f"🔴 {c['nombre']} - Debe: ${saldo}"):
                    pago = st.number_input(f"Monto que entrega {c['nombre']}", min_value=0, max_value=int(saldo), key=f"p_{c['nombre']}")
                    if st.button(f"Registrar Entrega de {c['nombre']}", key=f"b_{c['nombre']}"):
                        if enviar_datos({"tipo": "cobro", "cliente": c['nombre'], "monto": pago}): st.rerun()
            else: st.write(f"🟢 {c['nombre']} (Al día)")

    # --- TAB 3: REPARTO (LISTA DE ENTREGAS) ---
    with tabs[2]:
        st.subheader("🛵 Pedidos en Camino")
        if not envios: st.info("No hay envíos pendientes.")
        for e in envios:
            with st.container(border=True):
                st.write(f"**Cliente:** {e['cliente']} | **Monto:** ${e['total']}")
                st.write(f"📍 {e['direccion']}")
                if st.button("✅ Marcar como Entregado", key=f"env_{e['id']}"):
                    if enviar_datos({"tipo": "estado_envio", "id": e['id']}): st.rerun()

    # --- TAB 4: INTELIGENCIA (BUSCADOR WHATSAPP) ---
    with tabs[3]:
        st.subheader("🔍 Radar de Clientes y Ofertas")
        it = st.text_input("¿Qué producto buscamos? (Ej: Coca)")
        if it:
            interesados = list(set([h['cliente'] for h in historial if it.lower() in str(h['detalle']).lower() and h['cliente'] != ""]))
            for cli in interesados:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {cli}")
                c_info = next((item for item in clis if item["nombre"] == cli), None)
                if c_info and c_info.get("tel"):
                    tel = str(c_info["tel"]).replace("+", "").replace(" ", "")
                    col2.markdown(f"[💬 WhatsApp](https://wa.me/{tel})")

    # --- TAB 5: BALANCE (CIERRE Y WHATSAPP) ---
    with tabs[4]:
        st.header("📊 Resumen de Caja")
        v_tot = bal.get('ventasHoy', 0)
        efec = bal.get('efectivo', 0)
        mp = bal.get('mercadoPago', 0)
        fia = bal.get('fiados', 0)

        col1, col2, col3 = st.columns(3)
        col1.metric("💵 Efectivo", f"${efec}")
        col2.metric("💳 Mercado Pago", f"${mp}")
        col3.metric("📝 Fiados Nuevos", f"${fia}")

        st.divider()
        # Reporte Dinámico para WhatsApp
        reporte = (f"*CIERRE {datetime.now().strftime('%d/%m/%Y')}*%0A"
                   f"💰 Total Ventas: ${v_tot}%0A"
                   f"💵 Efectivo: ${efec}%0A"
                   f"💳 MP: ${mp}%0A"
                   f"📝 Fiados: ${fia}%0A"
                   f"👤 Responsable: {st.session_state['usuario']}")
        
        st.markdown(f'<a href="https://wa.me/?text={reporte}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">📤 ENVIAR REPORTE DIARIO</button></a>', unsafe_allow_html=True)
        
        if top:
            st.subheader("🔥 Top 5 más vendidos")
            df_top = pd.DataFrame(top.items(), columns=['Producto', 'Cant']).sort_values(by='Cant', ascending=False)
            st.table(df_top.head(5))

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False; st.rerun()
