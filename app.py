import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión Familiar PRO", layout="wide")

# URL de tu Script de Google (La que ya configuramos)
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

# --- FUNCIONES DE CONEXIÓN ---
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
        "producto_nombre": producto_nombre
    }
    try:
        r = requests.post(URL_SCRIPT, params=payload, timeout=15)
        return r.status_code == 200
    except:
        return False

# --- SISTEMA DE LOGUEO ---
usuarios_fijos = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}

if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<h2 style='text-align: center;'>🔐 Acceso Gestión</h2>", unsafe_allow_html=True)
    user = st.selectbox("¿Quién sos?", ["Seleccionar...", "Celeste", "Agu", "Mamá"])
    if user != "Seleccionar...":
        pin = st.text_input(f"PIN de {user}:", type="password", max_chars=4)
        if st.button("ENTRAR", use_container_width=True):
            if pin == usuarios_fijos.get(user):
                st.session_state['autenticado'] = True
                st.session_state['usuario'] = user
                st.rerun()
            else:
                st.error("PIN incorrecto")

# --- PANEL PRINCIPAL (Solo si está autenticado) ---
else:
    st.title(f"🏪 Panel de Ventas - {st.session_state['usuario']}")
    
    # Intentamos cargar productos del Excel
    with st.spinner("Actualizando precios y stock..."):
        lista_productos = obtener_productos()
    
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🛒 Registrar Venta")
        with st.container(border=True):
            nombres_prod = [p['nombre'] for p in lista_productos]
            prod_sel = st.selectbox("Elegí Producto:", ["Venta Manual"] + nombres_prod)
            
            monto_final = 0
            detalle_final = ""
            prod_nombre_para_stock = ""

            if prod_sel == "Venta Manual":
                monto_final = st.number_input("Precio ($):", min_value=0, step=50, value=0)
                detalle_final = st.text_input("Detalle de la venta:", placeholder="Ej: Varios panadería")
            else:
                # Buscamos los datos del producto elegido
                datos_p = next(p for p in lista_productos if p['nombre'] == prod_sel)
                
                # REEMPLAZO ANTI-ERROR: Validamos que el precio sea un número válido
                try:
                    # Usamos float por si hay decimales, y luego int
                    precio_sugerido = int(float(datos_p.get('venta', 0)))
                except (ValueError, TypeError):
                    precio_sugerido = 0
                
                monto_final = st.number_input("Confirmar Precio ($):", value=precio_sugerido)
                
                # Mostramos stock si existe
                stock_actual = datos_p.get('stock', 0)
                st.info(f"Stock disponible: {stock_actual} unidades")
                
                detalle_final = f"Producto: {prod_sel}"
                prod_nombre_para_stock = prod_sel

            metodo_pago = st.radio("Forma de pago:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)

            if st.button("🚀 REGISTRAR VENTA", use_container_width=True):
                if monto_final > 0 or "CONSUMO" in detalle_final:
                    with st.spinner("Guardando..."):
                        exito = enviar_venta(st.session_state['usuario'], monto_final, detalle_final, metodo_pago, prod_nombre_para_stock)
                    
                    if exito:
                        st.success("¡Venta registrada con éxito!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Error de conexión con el Excel.")
                else:
                    st.warning("Ingresá un monto válido.")

    with col2:
        st.subheader("🏠 Consumo de la Casa")
        with st.container(border=True):
            st.write("Registrá lo que retiren para uso personal (no suma dinero).")
            if nombres_prod:
                prod_casa = st.selectbox("¿Qué retiraron?", nombres_prod, key="casa_select")
                if st.button("🍎 REGISTRAR COMO CONSUMO", use_container_width=True):
                    with st.spinner("Actualizando stock..."):
                        if enviar_venta(st.session_state['usuario'], 0, f"CONSUMO CASA: {prod_casa}", "CASA", prod_casa):
                            st.warning(f"Se descontó 1 {prod_casa} del inventario.")
                            st.rerun()
            else:
                st.write("Cargá productos en el Excel para ver esta sección.")

    st.sidebar.divider()
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['autenticado'] = False
        st.rerun()
