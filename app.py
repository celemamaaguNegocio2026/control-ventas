# Busca la pestaña tabs[4] (Balance) en tu app.py y reemplazala con esto:

    with tabs[4]:
        st.header("📊 Cierre de Caja Diario")
        
        b = bal # Simplificamos
        v_total = b.get('ventasHoy', 0)
        efectivo = b.get('efectivo', 0)
        mp = b.get('mercadoPago', 0)
        fiados = b.get('fiados', 0)
        ahorro = v_total * 0.05
        
        col1, col2, col3 = st.columns(3)
        col1.metric("💵 Efectivo", f"${efectivo}")
        col2.metric("💳 Mercado Pago", f"${mp}")
        col3.metric("📝 Fiados Hoy", f"${fiados}")

        st.divider()
        
        # --- BOTÓN DE WHATSAPP ---
        texto_reporte = (
            f"*CIERRE DE CAJA - {datetime.now().strftime('%d/%m/%Y')}*%0A"
            f"---------------------------------%0A"
            f"💰 *Ventas Totales:* ${v_total}%0A"
            f"💵 *Efectivo en Caja:* ${efectivo}%0A"
            f"💳 *Mercado Pago:* ${mp}%0A"
            f"📝 *Fiado Nuevo:* ${fiados}%0A"
            f"🏦 *Reserva Emergencia (5%):* ${ahorro:.2f}%0A"
            f"---------------------------------%0A"
            f"👤 Responsable: {st.session_state['usuario']}"
        )
        
        # Link de WhatsApp (Pone tu número o el del grupo de las 3)
        # Si es un grupo, podés mandarlo a tu propio número y de ahí reenviarlo
        st.markdown(f"""
            <a href="https://wa.me/?text={texto_reporte}" target="_blank">
                <button style="width:100%; background-color:#25D366; color:white; border:none; padding:15px; border-radius:10px; font-weight:bold; cursor:pointer;">
                    📤 ENVIAR REPORTE POR WHATSAPP
                </button>
            </a>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        with st.expander("🔐 Realizar Arqueo Ciego"):
            contado = st.number_input("¿Cuánto efectivo contaste?", min_value=0)
            if st.button("Validar Efectivo"):
                if contado == efectivo: st.success("¡Coincide perfecto!")
                else: st.error(f"Diferencia: ${contado - efectivo}")
