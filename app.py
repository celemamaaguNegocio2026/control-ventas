import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Gestión Familiar Business", layout="wide")

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

def obtener_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=15)
        return r.json() if r.status_code == 200 else {"productos": [], "clientes": []}
    except: return {"productos": [], "clientes": []}

def enviar_datos(payload):
    try:
        r = requests.post(URL_SCRIPT, params=payload, timeout=15)
        return r.status_code == 200
    except: return False

# --- LOGIN ---
usuarios = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso")
    u = st.selectbox("Usuario:", ["Seleccionar..."] + list(usuarios.keys()))
    if u != "Seleccionar...":
        p = st.text_input("PIN:", type="password")
        if st.button("ENTRAR"):
            if p == usuarios[u]:
                st.session_state.update({"autenticado": True, "usuario": u})
                st.rerun()
else:
    # --- CARGA DE DATOS ---
    with st.spinner("Sincronizando con Excel..."):
        datos = obtener_datos()
        prods = datos['productos']
        clis = datos['clientes']

    st.sidebar.title(f"👤 {st.session_state['usuario']}")
    
    tab1, tab2, tab3 = st.tabs(["💰 VENTAS", "📉 GASTOS", "👥 CLIENTES/COBROS"])

    with tab1:
        col_v1, col_v2 = st.columns(2)
        with col_v1:
            st.markdown("### Registrar Venta")
            nombres_p = [p['nombre'] for p in prods]
            sel_p = st.selectbox("Producto:", ["Manual"] + nombres_p)
            
            monto = 0
            if sel_p == "Manual":
                monto = st.number_input("Monto ($):", min_value=0, key="m_manual")
                desc = st.text_input("Detalle:", key="d_manual")
            else:
                p_data = next(item for item in prods if item['nombre'] == sel_p)
                monto = st.number_input("Precio ($):", value=int(float(p_data['venta'])), key="m_p")
                desc = f"Venta: {sel_p}"
                st.caption(f"Stock: {p_data['stock']}")

            metodo = st.radio("Pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
            
            cliente_sel = ""
            if metodo == "Fiado":
                cliente_sel = st.selectbox("¿A quién le fiamos?", [c['nombre'] for c in clis])
                c_data = next(item for item in clis if item['nombre'] == cliente_sel)
                if float(c_data['saldo']) >= float(c_data['limite']):
                    st.error(f"⚠️ {cliente_sel} superó su límite de de $ {c_data['limite']}")

            if st.button("🚀 GUARDAR VENTA"):
                payload = {
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario": st.session_state['usuario'],
                    "monto": monto,
                    "detalle": f"[{metodo}] {desc}",
                    "producto_nombre": "" if sel_p == "Manual" else sel_p,
                    "metodo": metodo,
                    "cliente": cliente_sel
                }
                if enviar_datos(payload):
                    st.success("¡Venta registrada!"); st.rerun()

    with tab2:
        st.subheader("Registro de Gastos")
        cat = st.selectbox("Categoría:", ["Mercadería", "Servicios", "Alquiler", "Sueldos", "Otros"])
        monto_g = st.number_input("Monto Gasto ($):", min_value=0)
        if st.button("REGISTRAR GASTO"):
            if enviar_datos({"tipo": "gasto", "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "usuario": st.session_state['usuario'], "categoria": cat, "monto": monto_g, "detalle": "Gasto registrado"}):
                st.error("Gasto anotado"); st.rerun()

    with tab3:
        st.subheader("Cuentas Pendientes")
        for c in clis:
            if float(c['saldo']) > 0:
                with st.expander(f"🔴 {c['nombre']} - DEBE: ${c['saldo']}"):
                    monto_pago = st.number_input(f"¿Cuánto paga {c['nombre']}?", min_value=0, max_value=int(float(c['saldo'])), key=f"pago_{c['nombre']}")
                    if st.button(f"Cobrar a {c['nombre']}", key=f"btn_{c['nombre']}"):
                        if enviar_datos({"tipo": "cobro", "cliente": c['nombre'], "monto": monto_pago}):
                            st.success(f"¡Cobro registrado! {c['nombre']} ahora debe menos."); st.rerun()
            else:
                st.write(f"🟢 {c['nombre']} está al día.")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False; st.rerun()
        st.session_state['autenticado'] = False
        st.rerun()
