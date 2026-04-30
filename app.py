import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Gestión Familiar PRO", layout="wide")

# URL de tu Script de Google
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

# --- FUNCIONES ---
def obtener_productos():
    """Trae la lista de productos desde la pestaña PRODUCTOS"""
    try:
        respuesta = requests.get(URL_SCRIPT, timeout=10)
        if respuesta.status_code == 200:
            return respuesta.json()
        return []
    except:
        return []

def enviar_venta(usuario, monto, detalle, metodo, producto_nombre=""):
    """Envía la venta al Excel y descuenta stock si corresponde"""
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    payload = {
        "fecha": fecha_hoy,
        "usuario": usuario,
        "monto": monto,
        "detalle": f"[{metodo}] {detalle}",
        "producto_nombre": producto_nombre  # Esto activa el descuento de stock
    }
    try:
        r = requests.post(URL_SCRIPT, params=payload, timeout=10)
        return r.status_code == 200
    except:
        return False

# --- LOGUEO ---
usuarios_fijos = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.title("🔐 Acceso")
    user = st.selectbox("Usuario:", ["Seleccionar...", "Celeste", "Agu", "Mamá"])
    if user != "Seleccionar...":
        pin = st.text_input("PIN:", type="password", max_chars=4)
        if st.button("ENTRAR"):
            if pin == usuarios_fijos.get(user):
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = user
                st.rerun()

# --- APP PRINCIPAL ---
else:
    st.title(f"🏪 Panel de {st.session_state['usuario']}")
    
    # --- CARGAR PRODUCTOS ---
    with st.spinner("Actualizando stock..."):
        lista_productos = obtener_productos()
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🛒 Registrar Venta")
        with st.container(border=True):
            # Buscador de productos
            nombres_prod = [p['nombre'] for p in lista_productos]
            prod_sel = st.selectbox("Elegí Producto:", ["Venta Manual"] + nombres_prod)
            
            monto_final = 0
            detalle_final = ""
            prod_nombre_para_stock = ""

            if prod_sel == "Venta Manual":
                monto_final = st.number_input("Precio ($):", min_value=0, step=50)
                detalle_final = st.text_input("Detalle (qué es?):")
            else:
                # Si elige un producto, busca el precio de venta en la lista
                datos_p = next(p for p in lista_productos if p['nombre'] == prod_sel)
                monto_final = st.number_input("Precio ($):", value=int(datos_p['venta']))
                st.info(f"Stock actual: {datos_p['stock']} unidades")
                detalle_final = f"Producto: {prod_sel}"
                prod_nombre_para_stock = prod_sel

            metodo_pago = st.radio("Forma de pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)

            if st.button("🚀 REGISTRAR", use_container_width=True):
                if monto_final > 0:
                    if enviar_venta(st.session_state['usuario'], monto_final, detalle_final, metodo_pago, prod_nombre_para_stock):
                        st.success("¡Venta guardada y stock actualizado!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Error al conectar con Google.")

    with col2:
        st.subheader("🏠 Consumo de la Casa")
        with st.container(border=True):
            st.write("Usa esto para lo que saquen ustedes.")
            prod_casa = st.selectbox("¿Qué sacaron?", nombres_prod, key="casa")
            if st.button("🍎 REGISTRAR CONSUMO"):
                if enviar_venta(st.session_state['usuario'], 0, f"CONSUMO CASA: {prod_casa}", "CASA", prod_casa):
                    st.warning(f"Se descontó 1 {prod_casa} del stock.")
                else:
                    st.error("Error.")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()
