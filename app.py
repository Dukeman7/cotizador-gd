if btn_calcular:
    prom, techo, suelo, L_input = calcular_precios(bw_input)

    # --- MOSTRAR RESULTADOS ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("PRECIO SUGERIDO", f"${prom:.2f}")
    c2.metric("LÍMITE MÁXIMO (Techo)", f"${techo:.2f}", delta_color="inverse")
    c3.metric("LÍMITE MÍNIMO (Suelo)", f"${suelo:.2f}", delta_color="normal")

    st.info(f"💡 **Nota para el vendedor:** Usted tiene un margen de negociación de **${techo-suelo:.2f}** por Mbps.")

    # --- GENERACIÓN DE GRÁFICA ---
    bw_range = np.logspace(np.log10(10), np.log10(q), 500)
    L_range = k_log + np.log10(bw_range / q)
    
    y_prom = (A / np.power(bw_range, n)) + C - L_range
    y_techo = y_prom + C_sup - (k_sup * L_range)
    y_suelo = y_prom - C_inf + (k_inf * L_range)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(bw_range, y_prom, color='blue', linewidth=2, label='Precio sugerido') 
    ax.plot(bw_range, y_techo, '--', color='red', alpha=0.6, label='Precio Techo') 
    ax.plot(bw_range, y_suelo, '--', color='green', alpha=0.6, label='Precio Suelo') 
    ax.fill_between(bw_range, y_suelo, y_techo, color='gray', alpha=0.1, label='Banda de Negociación')
    
    # El Punto de la Cotización Actual
    ax.scatter(bw_input, prom, color='gold', s=180, edgecolors='black', zorder=5, label='Cotización Actual')
    
    ax.set_xscale('log')
    ax.set_ylim(0, 35)
    ax.set_xlabel("Capacidad (Mbps)")
    ax.set_ylabel("USD / Mbps")
    ax.legend()
    ax.set_title("Matriz de Ubicación de Oferta Comercial")
    
    st.pyplot(fig)

# --- BARRA LATERAL ---
st.sidebar.markdown("---")
st.sidebar.write("🛠️ **Desarrollo Técnico: Mago Luis**")
st.sidebar.write("Versión del Algoritmo: 3.0 (Balanced Mode)")
