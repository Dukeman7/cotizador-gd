import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IUFO ENGINE 2026", layout="wide")

# --- MODO GUMERSINDA: BARRA LATERAL DE CONTROL ---
st.sidebar.header("🛠️ Parámetros del Algoritmo")

# Coeficientes Maestros
col_a, col_b = st.sidebar.columns(2)
with col_a:
    A = st.number_input("Coeficiente A", value=57.70, format="%.2f")
    C = st.number_input("Constante C", value=2.95, format="%.2f")
    q = st.number_input("Escala q (Capacidad Max)", value=100400)
with col_b:
    n = st.number_input("Exponente n", value=0.69, format="%.2f")
    k_log = st.number_input("k_log", value=2.10, format="%.2f")

st.sidebar.subheader("📐 Definición de Bandas")
C_sup = st.sidebar.number_input("C_sup (Techo)", value=3.20, format="%.2f")
k_sup = st.sidebar.number_input("k_sup", value=1.05, format="%.2f")
C_inf = st.sidebar.number_input("C_inf (Suelo)", value=1.00, format="%.2f")
k_inf = st.sidebar.number_input("k_inf", value=0.35, format="%.2f")

st.sidebar.header("📊 Ajustes de Visualización")
titulo_grafica = st.sidebar.text_input("Título de la Gráfica", "AUDITORÍA ESTRATÉGICA IUFO 2026")
x_max_input = st.sidebar.number_input("Límite Máx X (Mbps)", value=30000)
y_max_input = st.sidebar.number_input("Límite Máx Y ($/Mbps)", value=60)

# --- CUERPO PRINCIPAL ---
st.title(f"🛡️ {titulo_grafica}")

# Entrada de Datos Manual
st.subheader("📝 Datos del Portafolio")
data_placeholder = (
    "10, 20.00, 1\n"
    "20, 20.00, 2\n"
    "100, 15.00, 1\n"
    "1024, 3.00, 12\n"
    "10240, 1.30, 4\n"
    "23552, 1.04, 1"
)
raw_data = st.text_area("Ingresa: Mbps, Precio_USD, N_Clientes (un plan por línea)", value=data_placeholder, height=150)

# --- LÓGICA DE CÁLCULO ---
def iufo_calc(bw):
    # Ecuaciones originales mantenidas tal cual
    L = k_log + np.log10(bw / q)
    p_prom = (A / np.power(bw, n)) + C - L
    p_techo = p_prom + C_sup - (k_sup * L)
    p_suelo = p_prom - C_inf + (k_inf * L)
    return p_prom, p_techo, p_suelo

try:
    # Procesar datos ingresados
    df = pd.read_csv(StringIO(raw_data), names=['bw', 'price', 'n_clients'])
    
    # Generar Curvas
    bw_range = np.logspace(0, np.log10(x_max_input), 1000)
    p_prom, p_techo, p_suelo = iufo_calc(bw_range)

    # --- PLOTTING ---
    fig, ax = plt.subplots(figsize=(12, 7))

    # Dibujar Bandas
    ax.plot(bw_range, p_prom, color='#004488', linewidth=2.5, label='Precio Sugerido IUFO', zorder=2)
    ax.plot(bw_range, p_techo, '--', color='#CC0000', alpha=0.5, label='Límite Techo (Máx)')
    ax.plot(bw_range, p_suelo, '--', color='#008800', alpha=0.5, label='Límite Suelo (Mín)')
    ax.fill_between(bw_range, p_suelo, p_techo, color='#004488', alpha=0.1, label='Banda de Negociación')

    # Dibujar Puntos (Tamaño proporcional a n_clients)
    scatter_sizes = df['n_clients'] * 100 # Factor de escala para visibilidad
    ax.scatter(df['bw'], df['price'], s=scatter_sizes, color='#004488', 
               edgecolors='white', linewidth=1.5, alpha=0.8, label='Clientes en el plan', zorder=3)

    # REGLAS ESTRICTAS: Origen (0,0) y Escala Lineal en Y
    ax.set_xscale('log')
    ax.set_yscale('linear') # Y Lineal
    
    ax.set_xlim(1, x_max_input) # X parte de 1 por ser logarítmica
    ax.set_ylim(0, y_max_input) # Y parte de 0 estrictamente
    
    # Ajuste visual de ejes para que se vean en el origen
    ax.spines['left'].set_position(('data', 1
