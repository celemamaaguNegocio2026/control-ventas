import streamlit as st
import requests
from datetime import datetime
import pandas as pd

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Familiar MASTER Pro", layout="wide")
# REEMPLAZA ESTA URL CON LA TUYA REAL:
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

# --- SESIÓN Y LOGIN ---
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
    with st.spinner("Sincronizando con Excel..."):
        d = obtener_datos()
        prods = d.get('productos', [])
        clis = d.get('clientes', [])
        envios = d.get('envios', [])
        bal = d.get('balance', {'ventasHoy': 0, 'gastosMes': 0})
        historial = d.get('historial', [])
        top = d.get('topVentas', {})

    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    tabs = st.tabs(["💰 VENTAS", "👥 CLIENTES", "🛵 REPARTO", "🔍 INTELIGENCIA", "📊 BALANCE"])

    # --- TAB 1: VENTAS ---
    with tabs[0]:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.subheader("Registrar Venta")
            nombres_p = [p['nombre'] for p in prods]
            sel_p = st.selectbox("Producto:", ["Manual"] + nombres_p)
            
            if sel_p != "Manual":
                p_data = next(item for item in prods if item['nombre'] == sel_p)
                try:
                    precio_sug = int(float(str(p_data.get('venta', '0')).replace(',', '.')))
                except: precio_sug = 0
                monto = st.number_input("Precio ($):", value=precio_sug, key="m_p_val")
                # Alerta de Stock
                stock_actual = p_data.get('stock', 0)
                if stock_actual <= 3:
                    st.error(f"⚠️ ¡SOLO QUEDAN {stock_actual}! Reponer stock.")
                else: st.info(f"Stock: {stock_actual}")
                desc = f"Venta: {sel_p}"
                prod_nombre_stock = sel_p
            else:
                monto = st.number_input("Monto ($):", min_value=0, key="m_man")
                desc = st.text_input("Detalle:", key="d_man")
                prod_nombre_stock = ""

            metodo = st.radio("Pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
            cliente_sel = st.selectbox("¿Quién compra?", [c['nombre'] for c in clis]) if metodo == "Fiado" else ""
            
            es_envio = st.checkbox("¿Es para enviar a domicilio?")
            direccion = st.text_input("Dirección:") if es_envio else ""

            if st.button("🚀 GUARDAR"):
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

    # --- TAB 2: CLIENTES (Restaurado) ---
    with tabs[1]:
        st.subheader("Estado de Cuentas")
        if not clis: st.info("Cargá clientes en el Excel.")
        for c in clis:
            saldo = float(c.get('saldo', 0))
            if saldo > 0:
                with st.expander(f"🔴 {c['nombre']} - Debe: ${saldo}"):
                    pago = st.number_input(f"Abono de {c['nombre']}", min_value=0, max_value=int(saldo), key=f"p_{c['nombre']}")
                    if st.button(f"Cobrar", key=f"b_{c['nombre']}"):
                        if enviar_datos({"tipo": "cobro", "cliente": c['nombre'], "monto": pago}): 
                            st.success("Cobro registrado"); st.rerun()
            else:
                st.write(f"🟢 {c['nombre']} (Al día)")

    # --- TAB 3: REPARTO (Restaurado) ---
    with tabs[2]:
        st.subheader("🛵 Envíos por entregar")
        if not envios:
            st.info("No hay pedidos en camino.")
        else:
            for e in envios:
                with st.container(border=True):
                    st.write(f"**Cliente:** {e['cliente']} | **Cobrar:** ${e['total']}")
                    st.write(f"🏠 {e['direccion']}")
                    if st.button(f"Entregado ✅", key=f"env_{e['id']}"):
                        if enviar_datos({"tipo": "estado_envio", "id": e['id']}):
                            st.rerun()

    # --- TAB 4: INTELIGENCIA ---
    with tabs[3]:
        st.header("🔍 Radar de Clientes")
        item_buscado = st.text_input("Buscador de ofertas (Ej: Coca)")
        if item_buscado:
            interesados = list(set([h['cliente'] for h in historial if item_buscado.lower() in h['detalle'].lower() and h['cliente'] != ""]))
            for c in interesados:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {c}")
                c_info = next((item for item in clis if item["nombre"] == c), None)
                if c_info and c_info.get("tel"):
                    tel = str(c_info["tel"]).replace("+", "").replace(" ", "")
                    col2.markdown(f"[💬 WhatsApp](https://wa.me/{tel})")

    # --- TAB 5: BALANCE ---
    with tabs[4]:
        st.header("📊 Cierre de Caja")
        v_hoy = bal.get('ventasHoy', 0)
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Ventas Hoy", f"${v_hoy}")
        col_m2.metric("Gastos Mes", f"${bal.get('gastosMes', 0)}")
        
        with st.expander("🔐 Arqueo Ciego"):
            plata_contada = st.number_input("Efectivo en mano:", min_value=0)
            if st.button("Verificar"):
                if plata_contada == v_hoy: st.success("¡Cerró perfecto!")
                else: st.error(f"Diferencia de: ${plata_contada - v_hoy}")
        
        if top:
            st.subheader("🔥 Más vendidos")
            df_top = pd.DataFrame(top.items(), columns=['Prod', 'Cant']).sort_values(by='Cant', ascending=False)
            st.table(df_top.head(5))

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False; st.rerun()
