import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="COTIZADOR IUFO-GD 2026", layout="centered")

# --- ESTILO CUSTOM (Branding Gold Data) ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; background-color: #004488; color: white; }
    .reportview-container .main .block-container{ padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ COTIZADOR IUFO-GD 2026")
st.subheader("Servicio de Internet Urbano en Fibra Óptica")

# --- MATRIZ DE PARÁMETROS MAESTRA (Baseline v3.0) ---
A, n, C, k_log, q = 57.70, 0.69, 2.95, 2.10, 100400
C_sup, k_sup, C_inf, k_inf = 3.20, 1.05, 1.00, 0.35

# --- INTERFAZ DE ENTRADA ---
with st.container():
    col1, col2 = st.columns([2, 1])
    with col1:
        bw_input = st.number_input("Capacidad a vender (Mbps):", min_value=10.0, max_value=100400.0, value=100.0, step=10.0)
    with col2:
        st.write("##") # Espaciador
        btn_calcular = st.button("CALCULAR COTIZACIÓN")

# --- LÓGICA DE CÁLCULO ---
def calcular_precios(bw):
    L = k_log + np.log10(bw / q)
    p_prom = (A / np.power(bw, n)) + C - L
    p_techo = p_prom + C_sup - (k_sup * L)
    p_suelo = p_prom - C_inf + (k_inf * L)
    return p_prom, p_techo, p_suelo, L

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
    ax.plot(bw_range, y_prom, color='blue', alpha=0.5, label='Promedio')
    ax.plot(bw_range, y_techo, '--', color='red', alpha=0.3)
    ax.plot(bw_range, y_suelo, '--', color='green', alpha=0.3)
    ax.fill_between(bw_range, y_suelo, y_techo, color='gray', alpha=0.1, label='Banda de Negociación')
    
    # El Punto de la Cotización Actual
    ax.scatter(bw_input, prom, color='gold', s=150, edgecolors='black', zorder=5, label='Cotización Actual')
    
    ax.set_xscale('log')
    ax.set_ylim(0, 35)
    ax.set_xlabel("Capacidad (Mbps)")
    ax.set_ylabel("USD / Mbps")
    ax.legend()
    ax.set_title("Ubicación de la Oferta en la Matriz Regulatoria")
    
    st.pyplot(fig)

st.sidebar.markdown("---")
st.sidebar.write("🔒 **Propiedad Intelectual: GOLD DATA 2026**")
st.sidebar.write("Versión del Algoritmo: 3.0 (Anchor Balanced)")
