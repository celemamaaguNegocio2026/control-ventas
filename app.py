# (Dentro de la pestaña tabs[4] de tu app.py, reemplazá el contenido por este)

    with tabs[4]:
        st.header("📊 Balance y Ganancia Real")
        
        ventas_hoy = bal.get('ventasHoy', 0)
        ganancia_bruta = bal.get('gananciaEstimadaHoy', 0)
        ahorro_emergencia = ventas_hoy * 0.05
        disponible = ventas_hoy - ahorro_emergencia

        col_met1, col_met2, col_met3 = st.columns(3)
        
        with col_met1:
            st.metric("Ventas Totales Hoy", f"${ventas_hoy}")
        with col_met2:
            st.metric("Ahorro Emergencia (5%)", f"${ahorro_emergencia:.2f}", delta="- Reserva")
        with col_met3:
            st.metric("Caja Disponible", f"${disponible:.2f}")

        st.divider()
        
        st.subheader("💡 Ganancia Estimada del Día")
        if ganancia_bruta > 0:
            st.success(f"Después de cubrir el costo de mercadería, hoy ganaste: **${ganancia_bruta - ahorro_emergencia:.2f}**")
            st.caption("Nota: A esto restale los gastos fijos (luz, alquiler) al final del mes.")
        else:
            st.info("Cargá los 'Costos' en tu Excel para ver la ganancia real aquí.")

        st.divider()
        st.subheader("💰 Reparto del Plus")
        if ventas_hoy > 30000: # Suponiendo que la meta es 30.000
            sobrante = ventas_hoy - 30000
            cada_una = sobrante / 3
            st.balloons()
            st.write(f"¡Superaron la meta! Sobraron **${sobrante}**.")
            st.write(f"Les toca un plus de **${cada_una:.2f}** a cada una (Celeste, Agu y Mamá).")
        else:
            faltante = 30000 - ventas_hoy
            st.warning(f"Faltan **${faltante}** para llegar a la meta y empezar a repartir el plus.")
