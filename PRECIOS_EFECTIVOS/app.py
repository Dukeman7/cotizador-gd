import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from io import StringIO
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IUFO Precision Engine v4.4", layout="wide")

# Forzado de contraste vía CSS
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    div.stTextArea textarea { font-family: 'Courier New', monospace; font-size: 14px; color: #1C2833; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL ---
st.sidebar.header("🛠️ Parámetros del Algoritmo")
titulo_input = st.sidebar.text_input("Título del Reporte", "AUDITORÍA DE TARIFICACIÓN ESTRATÉGICA")

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

st.sidebar.subheader("📊 Ajustes Visuales")
x_max = st.sidebar.number_input("Máximo Mbps (X)", value=40000)
y_max = st.sidebar.number_input("Máximo $/Mbps (Y)", value=60)
factor_circulo = st.sidebar.slider("Escala de Círculos", 1, 100, 40)

def calc_curvas(bw):
    L = k_log + np.log10(bw / q)
    p_prom = (A / np.power(bw, n)) + C - L
    p_techo = p_prom + C_sup - (k_sup * L)
    p_suelo = p_prom - C_inf + (k_inf * L)
    return p_prom, p_techo, p_suelo

# --- ÁREA DE TRABAJO ---
st.subheader("📝 Datos del Portafolio")
raw_data = st.text_area("Pega celdas de Excel (Mbps  Precio  Clientes)", 
                        value="100  15.0  1\n1000  3.5  12\n10000  1.3  4", 
                        height=100)

try:
    clean_data = re.sub(r'[ \t]+', ',', raw_data.strip())
    df = pd.read_csv(StringIO(clean_data), names=['bw', 'price', 'n_clients'])
    
    bw_range = np.logspace(0, np.log10(x_max), 600)
    p_p, p_t, p_s = calc_curvas(bw_range)

    fig = go.Figure()

    # 1. Banda Sombreada
    fig.add_trace(go.Scatter(
        x=np.concatenate([bw_range, bw_range[::-1]]),
        y=np.concatenate([p_t, p_s[::-1]]),
        fill='toself',
        fillcolor='rgba(0, 100, 200, 0.06)', 
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip',
        name='Rango de Negociación'
    ))

    # 2. Curvas de Referencia (Colores más fuertes)
    fig.add_trace(go.Scatter(x=bw_range, y=p_p, name='Sugerido', line=dict(color='#154360', width=3)))
    fig.add_trace(go.Scatter(x=bw_range, y=p_t, name='Techo Máx.', line=dict(color='#943126', width=1.5, dash='dot')))
    fig.add_trace(go.Scatter(x=bw_range, y=p_s, name='Suelo Mín.', line=dict(color='#145A32', width=1.5, dash='dot')))

    # 3. Datos de Clientes (Borde blanco más grueso para que resalten)
    fig.add_trace(go.Scatter(
        x=df['bw'],
        y=df['price'],
        mode='markers',
        name='Portafolio Actual',
        marker=dict(
            size=df['n_clients'],
            sizemode='area',
            sizeref=2. * max(df['n_clients']) / (factor_circulo**2),
            color='#154360',
            line=dict(width=1.5, color='white'),
            opacity=0.9
        ),
        text=[f"<b>PLAN: {b} Mbps</b><br>Clientes: {int(c)}<br>Precio: ${p}/Mbps" 
              for c, b, p in zip(df['n_clients'], df['bw'], df['price'])],
        hoverinfo='text'
    ))

    # --- DISEÑO DE INTERFAZ (LAYOUT v4.4 HIGH VISIBILITY) ---
    fig.update_layout(
        title={
            'text': f"<b>{titulo_input.upper()}</b>",
            'y': 0.96, 'x': 0.5, 'xanchor': 'center', 'yanchor': 'top',
            'font': {'size': 24, 'family': 'Arial Black', 'color': '#1C2833'}
        },
        template='plotly_white',
        paper_bgcolor='white', plot_bgcolor='white',
        height=800,
        margin=dict(l=80, r=60, b=100, t=120),
        
        # LEYENDA (Fuente más grande y borde definido)
        legend=dict(
            orientation="v", yanchor="top", y=0.98, xanchor="right", x=0.98,
            bgcolor="rgba(255, 255, 255, 0.9)",
            bordercolor="#1C2833", borderwidth=1.2,
            font=dict(size=13, family='Arial Bold', color='#1C2833')
        ),
        
        # HOVER (Mucho más visible)
        hoverlabel=dict(
            bgcolor="white",
            font_size=15, # Fuente más grande
            font_family="Arial",
            font_color="#1C2833",
            bordercolor="#1C2833"
        )
    )

    # EJES (Escalas y nombres con máximo contraste)
    fig.update_xaxes(
        type="log", 
        title="CAPACIDAD CONTRATADA (Mbps)", 
        title_font=dict(size=15, family='Arial Black', color='#1C2833'),
        range=[0, np.log10(x_max)],
        zeroline=True, zerolinecolor='#1C2833', linewidth=2, 
        gridcolor='#EBEDEF', 
        tickfont=dict(size=13, family='Arial Bold', color='#1C2833') # Escalas visibles
    )
    fig.update_yaxes(
        title="PRECIO UNITARIO (USD / Mbps)", 
        title_font=dict(size=15, family='Arial Black', color='#1C2833'),
        range=[0, y_max],
        zeroline=True, zerolinecolor='#1C2833', linewidth=2, 
        gridcolor='#EBEDEF', 
        tickfont=dict(size=13, family='Arial Bold', color='#1C2833') # Escalas visibles
    )

    st.plotly_chart(fig, use_container_width=True, theme=None)

except Exception as e:
    st.info("💡 Pega tus datos de Excel para activar el análisis v4.4")

st.sidebar.markdown("---")
st.sidebar.caption("🔍 Gumersinda High-Vis v4.4 | By Luis Duque")
