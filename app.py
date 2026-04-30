import streamlit as st
import requests
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Gestión MASTER Pro", layout="wide")
URL_SCRIPT = "TU_URL_AQUI" # Poné tu URL real acá

def obtener_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=15)
        return r.json() if r.status_code == 200 else {}
    except: return {}

def enviar_datos(p):
    try: return requests.post(URL_SCRIPT, params=p, timeout=15).status_code == 200
    except: return False

# --- SESIÓN Y LOGIN ---
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
else:
    with st.spinner("Sincronizando..."):
        d = obtener_datos()
        prods = d.get('productos', [])
        clis = d.get('clientes', [])
        envios = d.get('envios', [])
        bal = d.get('balance', {'ventasHoy': 0})
        historial = d.get('historial', [])
        top = d.get('topVentas', {})

    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    tabs = st.tabs(["💰 VENTAS", "👥 CLIENTES", "🛵 REPARTO", "🔍 INTELIGENCIA", "📊 BALANCE"])

    with tabs[0]: # VENTAS CON ALERTA
        st.subheader("Nueva Venta")
        nombres_p = [p['nombre'] for p in prods]
        sel_p = st.selectbox("Producto:", ["Manual"] + nombres_p)
        
        if sel_p != "Manual":
            p_data = next(item for item in prods if item['nombre'] == sel_p)
            stock_actual = p_data.get('stock', 0)
            if stock_actual <= 3:
                st.error(f"⚠️ ¡SOLO QUEDAN {stock_actual} UNIDADES! Reponer urgente.")
            else:
                st.info(f"Stock disponible: {stock_actual}")

        monto_v = st.number_input("Monto ($):", min_value=0)
        if st.button("GUARDAR VENTA"):
            # Lógica de guardado...
            st.success("Venta registrada")

    with tabs[3]: # INTELIGENCIA CON WHATSAPP
        st.header("🔍 Radar de Clientes")
        item = st.text_input("Buscar quién compró:")
        if item:
            lista = list(set([h['cliente'] for h in historial if item.lower() in h['detalle'].lower()]))
            for c in lista:
                col1, col2 = st.columns([3, 1])
                col1.write(f"👤 {c}")
                # Buscamos el tel en la lista de clientes
                c_info = next((item for item in clis if item["nombre"] == c), None)
                if c_info and c_info.get("tel"):
                    tel = str(c_info["tel"]).replace("+", "").replace(" ", "")
                    col2.markdown(f"[💬 WhatsApp](https://wa.me/{tel}?text=Hola%20{c}!%20Tenemos%20oferta%20en%20{item})")

    with tabs[4]: # BALANCE CON RANKING
        st.header("Resultados")
        st.metric("Ventas Hoy", f"${bal['ventasHoy']}")
        
        st.subheader("🔥 Lo más vendido")
        if top:
            df_top = pd.DataFrame(top.items(), columns=['Producto', 'Ventas']).sort_values(by='Ventas', ascending=False)
            st.table(df_top.head(5))

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False; st.rerun()
