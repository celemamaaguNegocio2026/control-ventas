import streamlit as st
import gspread
from google.auth import default
import pandas as pd
from google.oauth2.service_account import Credentials

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Sistema de Ventas - Caro", layout="centered")

# --- CONEXIÓN CON GOOGLE SHEETS ---
# Usamos la URL de tu planilla
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1pSb1ttNGH4RTDgG11aMx23z177QMfXw9LUrLGPQu6vM/edit?usp=sharing"

def conectar_planilla():
    # Nota: Cuando lo subas a Streamlit Cloud, necesitaremos un paso extra de seguridad
    # Pero por ahora, este es el código base de tu App
    from google.colab import auth
    auth.authenticate_user()
    creds, _ = default()
    gc = gspread.authorize(creds)
    return gc.open_by_url(SPREADSHEET_URL)

# Intentar abrir la planilla
try:
    sh = conectar_planilla()
except:
    st.error("Esperando conexión con Google Sheets...")
    st.stop()

# --- DISEÑO DE LA APP ---
st.title("🚀 Sistema de Gestión Familiar")
st.write("Bienvenidas al centro de control.")

# Menú lateral
menu = ["🏠 Inicio", "📦 Inventario", "💰 Registrar Venta", "📊 Cuentas"]
choice = st.sidebar.selectbox("Menú", menu)

# --- SECCIÓN: INICIO ---
if choice == "🏠 Inicio":
    st.subheader("¡Hola equipo!")
    st.info("Seleccioná una opción en el menú de la izquierda para empezar.")
    st.write("Este sistema está conectado en tiempo real con tu Google Sheets.")

# --- SECCIÓN: INVENTARIO ---
elif choice == "📦 Inventario":
    st.subheader("📦 Stock en góndola")
    try:
        ws_inv = sh.worksheet("Inventario")
        datos = ws_inv.get_all_records()
        df = pd.DataFrame(datos)
        st.dataframe(df, use_container_width=True)
    except:
        st.warning("No se pudo cargar el inventario. Verificá la pestaña en tu Excel.")

# --- SECCIÓN: REGISTRAR VENTA ---
elif choice == "💰 Registrar Venta":
    st.subheader("💸 Nueva Venta")
    with st.form("formulario_venta"):
        vendedor = st.selectbox("¿Quién realiza la venta?", ["Agustina", "Celeste", "Mamá"])
        codigo = st.text_input("Código de Barras")
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        cuenta = st.selectbox("¿A dónde entra la plata?", 
                             ["Yoy", "Ualá", "Efectivo", "Galicia", "Personal Pay", "Supervielle", "Brubank"])
        
        boton_venta = st.form_submit_button("Confirmar Venta")
        
        if boton_venta:
            st.success(f"Venta de {vendedor} registrada. ¡Buen trabajo!")
            # Aquí mañana agregamos la lógica para que descuente stock solo

# --- SECCIÓN: CUENTAS ---
elif choice == "📊 Cuentas":
    st.subheader("💰 Saldo Actual en Cuentas")
    try:
        ws_cuentas = sh.worksheet("Cuentas")
        datos_cuentas = ws_cuentas.get_all_records()
        df_cuentas = pd.DataFrame(datos_cuentas)
        st.table(df_cuentas)
    except:
        st.error("No se pudo leer la pestaña 'Cuentas'.")