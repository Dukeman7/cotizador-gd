import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Calculador de Tarifas 2026", layout="wide")

# --- BARRA LATERAL (CONTROL TOTAL) ---
st.sidebar.header("🛠️ Configuración del Modelo")

# Título de la Gráfica
titulo_input = st.sidebar.text_input("Título de la Gráfica", "MATRIZ DE TARIFICACIÓN ESTRATÉGICA")

# Coeficientes
col1, col2 = st.sidebar.columns(2)
with col1:
    A = st.number_input("A", value=57.70, format="%.2f")
    C = st.number_input("C", value=2.95, format="%.2f")
    q = st.number_input("q (Max BW)", value=100400)
with col2:
    n = st.number_input("n", value=0.69, format="%.2f")
    k_log = st.number_input("k_log", value=2.10, format="%.2f")

st.sidebar.subheader("📐 Parámetros de Banda")
C_sup = st.sidebar.number_input("C_sup", value=3.20)
k_sup = st.sidebar.number_input("k_sup", value=1.05)
C_inf = st.sidebar.number_input("C_inf", value=1.00)
k_inf = st.sidebar.number_input("k_inf", value=0.35)

st.sidebar.subheader("📊 Límites de Ejes")
x_max = st.sidebar.number_input("Máximo X (Mbps)", value=40000)
y_max = st.sidebar.number_input("Máximo Y ($/Mbps)", value=60)

# --- CUERPO PRINCIPAL ---
st.title(titulo_input) # Título Editable

st.subheader("📝 Datos del Portafolio")
st.caption("Tip: Puedes copiar celdas de Excel y pegarlas aquí directamente.")
raw_data = st.text_area("Formato: Mbps   Precio   Clientes", 
                        value="100  15.0  1\n1000  3.5  12\n10000  1.3  4", height=150)

def iufo_calc(bw):
    L = k_log + np.log10(bw / q)
    p_prom = (A / np.power(bw, n)) + C - L
    p_techo = p_prom + C_sup - (k_sup * L)
    p_suelo = p_prom - C_inf + (k_inf * L)
    return p_prom, p_techo, p_suelo

try:
    # Procesamiento inteligente de datos (acepta tabs de Excel o comas)
    clean_data = re.sub(r'[ \t]+', ',', raw_data.strip())
    df = pd.read_csv(StringIO(clean_data), names=['bw', 'price', 'n_clients'])
    
    # Generar Curvas
    bw_range = np.logspace(0, np.log10(x_max), 1000)
    p_p, p_t, p_s = iufo_calc(bw_range)

    # Gráfico
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Curvas (Sin el nombre IUFO)
    ax.plot(bw_range, p_p, color='#004488', linewidth=2, label='Precio Sugerido')
    ax.plot(bw_range, p_t, '--', color='#CC0000', alpha=0.4, label='Límite Techo')
    ax.plot(bw_range, p_s, '--', color='#008800', alpha=0.4, label='Límite Suelo')
    ax.fill_between(bw_range, p_s, p_t, color='#004488', alpha=0.08, label='Banda de Negociación')

    # Puntos Proporcionales
    ax.scatter(df['bw'], df['price'], s=df['n_clients']*100, color='#004488', 
               edgecolors='white', linewidth=1, alpha=0.7, label='Clientes en el plan')

    # Configuración de Ejes Estricta
    ax.set_xscale('log')
    ax.set_yscale('linear') # Lineal en Y
    ax.set_xlim(1, x_max)
    ax.set_ylim(0, y_max)
    
    # Asegurar que el origen visual sea 0,0 (en log X=1)
    ax.spines['bottom'].set_position(('data', 0))
    ax.spines['left'].set_position(('data', 1))

    ax.set_xlabel("Capacidad (Mbps)")
    ax.set_ylabel("USD / Mbps")
    ax.grid(True, which="both", ls="-", alpha=0.1)
    ax.legend()

    st.pyplot(fig)
    
except Exception as e:
    st.warning("Esperando datos válidos para graficar...")

st.sidebar.markdown("---")
st.sidebar.caption("Modo Gumersinda v3.6 Final")
