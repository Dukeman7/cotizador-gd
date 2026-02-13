# --- TÍTULO NEUTRAL ---
st.title("🛡️ COTIZADOR DE PRECIOS PARA SERVICIO DE INTERNET URBANO")
st.subheader("Algoritmo de Tarificación Estratégica 2026")

# ... (dentro del bloque 'if btn_calcular' donde se genera la gráfica) ...

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(bw_range, y_prom, color='blue', linewidth=2, label='Precio sugerido') # Azul
    ax.plot(bw_range, y_techo, '--', color='red', alpha=0.6, label='Precio Techo') # Rojo
    ax.plot(bw_range, y_suelo, '--', color='green', alpha=0.6, label='Precio Suelo') # Verde
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

# --- BARRA LATERAL LIMPIA ---
st.sidebar.markdown("---")
st.sidebar.write("🛠️ **Desarrollo Técnico: Mago Luis**")
st.sidebar.write("Versión del Algoritmo: 3.0 (Balanced Mode)")
