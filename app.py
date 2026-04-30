import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Gestión Familiar MASTER v2", layout="wide")
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

def obtener_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=15)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def enviar_datos(p):
    try: return requests.post(URL_SCRIPT, params=p, timeout=15).status_code == 200
    except: return False

usuarios = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso")
    u = st.selectbox("Usuario:", ["Seleccionar..."] + list(usuarios.keys()))
    if u != "Seleccionar...":
        p = st.text_input("PIN:", type="password")
        if st.button("ENTRAR"):
            if p == usuarios[u]:
                st.session_state.update({"autenticado": True, "usuario": u}); st.rerun()
            else: st.error("PIN Incorrecto")
else:
    with st.spinner("Sincronizando sistema..."):
        d = obtener_datos()
        prods = d.get('productos', [])
        clis = d.get('clientes', [])
        envios = d.get('envios', [])
        bal = d.get('balance', {'ventasHoy': 0})
        historial = d.get('historial', [])

    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    tabs = st.tabs(["💰 VENTAS", "👥 CLIENTES", "🛵 REPARTO", "🔍 INTELIGENCIA", "📊 BALANCE"])

    # --- VENTAS, CLIENTES Y REPARTO (Código previo abreviado aquí por espacio) ---
    with tabs[0]:
        st.subheader("Registrar Venta")
        nombres_p = [p['nombre'] for p in prods]
        sel_p = st.selectbox("Producto:", ["Manual"] + nombres_p)
        metodo = st.radio("Pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
        monto_v = st.number_input("Monto ($):", min_value=0)
        if st.button("GUARDAR VENTA"):
            payload = {"fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "usuario": st.session_state['usuario'], "monto": monto_v, "detalle": f"[{metodo}] {sel_p}", "producto_nombre": "" if sel_p == "Manual" else sel_p, "metodo": metodo, "cliente": ""}
            if enviar_datos(payload): st.success("¡Venta!"); st.rerun()

    # --- NUEVA PESTAÑA: INTELIGENCIA (Buscador de Clientes) ---
    with tabs[3]:
        st.header("🔍 Buscador de Ofertas")
        item_buscado = st.text_input("¿Qué producto está en oferta? (Ej: Coca 500)")
        if item_buscado:
            compradores = list(set([h['cliente'] for h in historial if item_buscado.lower() in h['detalle'].lower() and h['cliente'] != ""]))
            if compradores:
                st.write(f"✅ Estos clientes compraron {item_buscado} antes. ¡Avisales!")
                for c in compradores: st.write(f"* {c}")
            else:
                st.info("No se encontraron clientes que hayan comprado eso todavía.")

    # --- BALANCE CON CIERRE CIEGO ---
    with tabs[4]:
        st.header("🏁 Cierre de Caja")
        
        # Primero el Cierre Ciego
        with st.expander("🔐 Realizar Arqueo de Caja (Cierre Ciego)"):
            st.write("Contá la plata en efectivo y poné el total abajo.")
            plata_en_mano = st.number_input("Efectivo contado ($):", min_value=0, key="ciego")
            if st.button("VERIFICAR CAJA"):
                v_hoy = bal['ventasHoy']
                if plata_en_mano == v_hoy:
                    st.success(f"¡Excelente! La caja coincide perfectamente con los ${v_hoy} registrados.")
                elif plata_en_mano > v_hoy:
                    st.warning(f"¡Sobran ${plata_en_mano - v_hoy}! Revisen si olvidaron anotar un gasto.")
                else:
                    st.error(f"¡Faltan ${v_hoy - plata_en_mano}! Revisen si alguien se olvidó de anotar una venta.")

        st.divider()
        st.subheader("📈 Resumen del Día")
        st.metric("Ventas de Hoy", f"${bal['ventasHoy']}")
        st.progress(min(bal['ventasHoy'] / 30000, 1.0))

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False; st.rerun()
