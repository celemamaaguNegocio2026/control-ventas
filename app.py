import streamlit as st
import requests
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA (ESTRICTO PARA MÓVIL) ---
st.set_page_config(page_title="Gestión", layout="centered")

# URL DE TU SCRIPT
URL_SCRIPT = "https://script.google.com/macros/s/AKfycbx0q2DspEDVcKu4khSyfFZZCrkuDohRntM5X2U-BVYUFYgGGtDLAVLLjQEI7vCUZOR3pA/exec"

# --- FUNCIONES ---
def obtener_datos():
    try:
        r = requests.get(URL_SCRIPT, timeout=10)
        return r.json()
    except:
        return st.session_state.get('backup', {"productos":[], "clientes":[], "balance":{}})

def enviar_datos(payload):
    try:
        return requests.post(URL_SCRIPT, params=payload, timeout=10).status_code == 200
    except: return False

# --- SESIÓN ---
if 'autenticado' not in st.session_state: st.session_state['autenticado'] = False

# --- PANTALLA DE LOGIN ---
if not st.session_state['autenticado']:
    st.title("🔑 ENTRAR")
    u = st.selectbox("QUIÉN SOS:", ["Seleccionar...", "Celeste", "Agu", "Mamá"])
    p = st.text_input("PIN:", type="password") # El teclado de PIN suele fallar menos
    if st.button("INGRESAR"):
        pins = {"Celeste": "1997", "Agu": "1995", "Mamá": "1975"}
        if p == pins.get(u):
            st.session_state.update({"autenticado": True, "usuario": u})
            st.rerun()
        else: st.error("PIN incorrecto")

# --- APP PRINCIPAL ---
else:
    d = obtener_datos()
    st.session_state['backup'] = d
    
    # NAVEGACIÓN SIMPLE (BOTONES ARRIBA, NO SIDEBAR)
    st.write(f"👤 **{st.session_state['usuario']}**")
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("🛒 VENTA"): st.session_state['seccion'] = "v"
    with c2:
        if st.button("👥 CLI"): st.session_state['seccion'] = "c"
    with c3:
        if st.button("📊 BAL"): st.session_state['seccion'] = "b"
    
    st.divider()
    seccion = st.session_state.get('seccion', "v")

    # --- SECCIÓN VENTAS ---
    if seccion == "v":
        st.subheader("🛒 NUEVA VENTA")
        
        prods = [p['nombre'] for p in d.get('productos', [])]
        sel = st.selectbox("¿QUÉ VENDISTE?", ["OTRO / MANUAL"] + prods)
        
        if sel == "OTRO / MANUAL":
            # Usamos un área de texto simple
            p_nom = st.text_area("NOMBRE DEL PRODUCTO:", height=60, placeholder="Escribí acá...")
            monto = st.number_input("PRECIO ($):", min_value=0, step=50)
        else:
            p_info = next(i for i in d['productos'] if i['nombre'] == sel)
            p_nom = sel
            try: sugerido = int(float(str(p_info.get('venta', 0)).replace(',','.')))
            except: sugerido = 0
            monto = st.number_input("CONFIRMAR PRECIO:", value=sugerido)
            st.write(f"Stock: {p_info.get('stock', 0)}")

        st.divider()
        met = st.radio("PAGO:", ["Efectivo", "Mercado Pago", "Fiado"], horizontal=True)
        
        cli = ""
        if met == "Fiado":
            cli = st.selectbox("¿A QUIÉN?", [c['nombre'] for c in d.get('clientes', [])])

        if st.button("🚀 GUARDAR AHORA"):
            if not p_nom:
                st.error("Falta el nombre")
            else:
                payload = {
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "usuario": st.session_state['usuario'],
                    "monto": monto,
                    "detalle": f"[{met}] {p_nom}",
                    "producto_nombre": p_nom,
                    "metodo": met,
                    "cliente": cli
                }
                if enviar_datos(payload):
                    st.success("✅ ¡LISTO!")
                    st.rerun()

    # --- SECCIÓN BALANCE ---
    elif seccion == "b":
        bal = d.get('balance', {})
        st.subheader("📊 BALANCE HOY")
        st.metric("TOTAL", f"${bal.get('ventasHoy', 0)}")
        st.write(f"💵 Efectivo: ${bal.get('efectivo', 0)}")
        st.write(f"💳 M.Pago: ${bal.get('mercadoPago', 0)}")
        st.write(f"📝 Fiado: ${bal.get('fiados', 0)}")

    # --- SECCIÓN CLIENTES ---
    elif seccion == "c":
        st.subheader("👥 DEUDAS")
        for c in d.get('clientes', []):
            if float(c.get('saldo', 0)) > 0:
                st.warning(f"{c['nombre']}: debe ${c['saldo']}")

    if st.button("🚪 SALIR"):
        st.session_state['autenticado'] = False
        st.rerun()
