import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from io import StringIO
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IUFO Interactive Engine", layout="wide")

# --- BARRA LATERAL ---
st.sidebar.header("🛠️ Parámetros del Algoritmo")
titulo_input = st.sidebar.text_input("Título de la Gráfica", "MATRIZ INTERACTIVA DE TARIFICACIÓN")

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
st.title(titulo_input)

st.subheader("📝 Datos del Portafolio")
raw_data = st.text_area("Pega celdas de Excel (Mbps  Precio  Clientes)", 
                        value="100  15.0  1\n1000  3.5  12\n10000  1.3  4", height=150)

def calc_curvas(bw):
    L = k_log + np.log10(bw / q)
    p_prom = (A / np.power(bw, n)) + C - L
    p_techo = p_prom + C_sup - (k_sup * L)
    p_suelo = p_prom - C_inf + (k_inf * L)
    return p_prom, p_techo, p_suelo

try:
    # Procesar datos
    clean_data = re.sub(r'[ \t]+', ',', raw_data.strip())
    df = pd.read_csv(StringIO(clean_data), names=['bw', 'price', 'n_clients'])
    
    # Generar Curvas para el fondo
    bw_range = np.logspace(0, np.log10(x_max), 500)
    p_p, p_t, p_s = calc_curvas(bw_range)

    # --- CREAR GRÁFICA INTERACTIVA CON PLOTLY ---
    fig = go.Figure()

    # 1. Banda de Negociación (Sombreado)
    fig.add_trace(go.Scatter(
        x=np.concatenate([bw_range, bw_range[::-1]]),
        y=np.concatenate([p_t, p_s[::-1]]),
        fill='toself',
        fillcolor='rgba(0, 68, 136, 0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip',
        showlegend=True,
        name='Banda de Negociación'
    ))

    # 2. Curvas de Referencia
    fig.add_trace(go.Scatter(x=bw_range, y=p_p, name='Precio Sugerido', line=dict(color='#004488', width=2)))
    fig.add_trace(go.Scatter(x=bw_range, y=p_t, name='Límite Techo', line=dict(color='#CC0000', width=1, dash='dash')))
    fig.add_trace(go.Scatter(x=bw_range, y=p_s, name='Límite Suelo', line=dict(color='#008800', width=1, dash='dash')))

    # 3. Puntos de Clientes (CON HOVER)
    fig.add_trace(go.Scatter(
        x=df['bw'],
        y=df['price'],
        mode='markers',
        name='Clientes en el plan',
        marker=dict(
            size=df['n_clients'] * 15, # Proporcional
            sizemode='area',
            sizeref=2.*max(df['n_clients'])/(40.**2),
            color='#004488',
            line=dict(width=1, color='white')
        ),
        text=[f"Clientes: {int(c)}<br>Capacidad: {b} Mbps<br>Precio: ${p}/Mbps" 
              for c, b, p in zip(df['n_clients'], df['bw'], df['price'])],
        hoverinfo='text'
    ))

    # Configuración de Ejes (Origen 0,0 y Lineal en Y)
    fig.update_xaxes(type="log", title="Capacidad contratada (Mbps)", range=[0, np.log10(x_max)], 
                     gridcolor='rgba(0,0,0,0.1)', zeroline=True, zerolinecolor='black')
    fig.update_yaxes(title="Precio Unitario (USD / Mbps)", range=[0, y_max], 
                     gridcolor='rgba(0,0,0,0.1)', zeroline=True, zerolinecolor='black')

    fig.update_layout(
        height=700,
        margin=dict(l=40, r=40, b=40, t=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor='white'
    )

    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.info("Copia y pega tus datos de Excel para activar la visión térmica del rifle.")

st.sidebar.markdown("---")
st.sidebar.caption("Modo Gumersinda v4.0 Interactivo")
