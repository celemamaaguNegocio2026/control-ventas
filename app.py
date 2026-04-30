import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión MASTER Final", layout="centered", initial_sidebar_state="expanded")

# CSS para dispositivos móviles
st.markdown("""
    <style>
    input { font-size: 16px !important; }
    .stNumberInput, .stTextInput { margin-bottom: -15px; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

def obtener_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=10)
        if r.status_code == 200:
            d = r.json()
            st.session_state['backup'] = d
            return d
        return st.session_state.get('backup', {})
    except:
        return st.session_state.get('backup', {"productos":[], "clientes":[], "balance":{}, "envios":[]})

def enviar_datos(payload):
    try:
        return requests.post(URL_SCRIPT, params=payload, timeout=10).status_code == 200
    except: return False

if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False

# --- ACCESO ---
if not st.session_state['autenticado']:
    st.title("🔐 Acceso")
    u = st.selectbox("Usuario:", ["Seleccionar...", "Celeste", "Agu", "Mamá"])
    p = st.text_input("PIN:", type="password")
    if st.button("INGRESAR"):
        pins = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
        if p == pins.get(u):
            st.session_state.update({"autenticado": True, "usuario": u})
            st.rerun()
        else: st.error("PIN incorrecto")

else:
    datos = obtener_datos()
    
    with st.sidebar:
        st.title(f"👋 {st.session_state['usuario']}")
        menu = st.radio("MENÚ", ["💰 Ventas", "👥 Clientes", "🛵 Repartos", "📊 Balance"])
        st.divider()
        if st.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()

    # --- SECCIÓN VENTAS (DISEÑO DE CARGA RÁPIDA) ---
    if menu == "💰 Ventas":
        st.header("🛒 Registrar Venta")
        
        cant = st.number_input("¿Cuántos productos lleva?", min_value=1, max_value=15, value=1)
        
        lista_venta = []
        total_acumulado = 0
        
        st.write("---")
        for i in range(int(cant)):
            col1, col2 = st.columns([2, 1])
            with col1:
                n = st.text_input(f"Producto {i+1}", key=f"n_{i}", placeholder="Nombre...")
            with col2:
                p = st.number_input(f"Precio {i+1}", key=f"p_{i}", min_value=0, step=10)
            
            if n:
                lista_venta.append(n)
                total_acumulado += p
        
        st.write("---")
        st.write(f"### TOTAL: ${total_acumulado}")
        
        metodo = st.radio("PAGO:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
        cliente_v = st.selectbox("CLIENTE:", [c['nombre'] for c in datos.get('clientes', [])]) if metodo == "Fiado" else ""
        
        # Opción de Envío integrada
        es_envio = st.checkbox("🛵 ¿Es para envío?")
        dire = st.text_input("Dirección:") if es_envio else ""

        if st.button("✅ GUARDAR VENTA TOTAL"):
            if not lista_venta:
                st.error("No hay productos cargados")
            else:
                detalle_txt = ", ".join(lista_venta)
                payload = {
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario": st.session_state['usuario'],
                    "monto": total_acumulado,
                    "detalle": f"[{metodo}] {detalle_txt}",
                    "producto_nombre": detalle_txt,
                    "metodo": metodo,
                    "cliente": cliente_v
                }
                if enviar_datos(payload):
                    if es_envio:
                        enviar_datos({"tipo": "envio", "cliente": cliente_v if cliente_v else "Venta Rapida", "direccion": dire, "total": total_acumulado})
                    st.success("¡Guardado!")
                    st.rerun()

    # --- SECCIÓN CLIENTES ---
    elif menu == "👥 Clientes":
        st.header("👥 Cuentas")
        for c in datos.get('clientes', []):
            saldo = float(c.get('saldo', 0))
            if saldo > 0:
                with st.expander(f"🔴 {c['nombre']} - ${saldo}"):
                    pago = st.number_input(f"Pago de {c['nombre']}", max_value=int(saldo), key=f"p_{c['nombre']}")
                    if st.button("Cobrar", key=f"b_{c['nombre']}"):
                        if enviar_datos({"tipo": "cobro", "cliente": c['nombre'], "monto": pago}):
                            st.rerun()

    # --- SECCIÓN REPARTOS ---
    elif menu == "🛵 Repartos":
        st.header("🛵 Envíos Pendientes")
        envios = datos.get('envios', [])
        if not envios: st.info("Todo entregado.")
        for e in envios:
            st.warning(f"📍 {e['direccion']}\n**{e['cliente']}** - ${e['total']}")
            if st.button(f"Entregado ✅", key=f"env_{e['id']}"):
                if enviar_datos({"tipo": "estado_envio", "id": e['id']}):
                    st.rerun()

    # --- SECCIÓN BALANCE ---
    elif menu == "📊 Balance":
        st.header("📊 Balance Hoy")
        bal = datos.get('balance', {})
        st.metric("TOTAL", f"${bal.get('ventasHoy', 0)}")
        c1, c2 = st.columns(2)
        c1.write(f"💵 Efectivo: ${bal.get('efectivo', 0)}")
        c2.write(f"💳 M.Pago: ${bal.get('mercadoPago', 0)}")
        st.write(f"📝 Fiados hoy: ${bal.get('fiados', 0)}")
