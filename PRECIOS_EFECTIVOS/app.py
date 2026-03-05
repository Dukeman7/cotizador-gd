import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from io import StringIO
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IUFO Precision Engine v4.3", layout="wide")

# Forzado de limpieza visual vía CSS
st.markdown("""
    <style>
    .main { background-color: #FFFFFF; }
    div.stTextArea textarea { font-family: 'Courier New', monospace; font-size: 14px; }
    .stPlotlyChart { border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- BARRA LATERAL (CONTROL DE MANDO) ---
st.sidebar.header("🛠️ Parámetros del Algoritmo")
titulo_input = st.sidebar.text_input("Título del Reporte", "AUDITORÍA DE TARIFICACIÓN ESTRATÉGICA")

# Coeficientes Maestros
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
factor_circulo = st.sidebar.slider("Escala de Círculos", 1, 100, 30)

# --- LÓGICA DE CÁLCULO ---
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
                        help="Soporta pegado directo de Excel (tabuladores)")

try:
    # Procesamiento con Regex para limpiar cualquier ruido de pegado
    clean_data = re.sub(r'[ \t]+', ',', raw_data.strip())
    df = pd.read_csv(StringIO(clean_data), names=['bw', 'price', 'n_clients'])
    
    # Generación de Curvas
    bw_range = np.logspace(0, np.log10(x_max), 600)
    p_p, p_t, p_s = calc_curvas(bw_range)

    # --- CONSTRUCCIÓN DEL GRÁFICO (v4.3 GUMER) ---
    fig = go.Figure()

    # 1. Banda Sombreada (Suave)
    fig.add_trace(go.Scatter(
        x=np.concatenate([bw_range, bw_range[::-1]]),
        y=np.concatenate([p_t, p_s[::-1]]),
        fill='toself',
        fillcolor='rgba(0, 100, 200, 0.04)', # Azul muy tenue
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip',
        name='Rango de Negociación'
    ))

    # 2. Curvas de Referencia
    fig.add_trace(go.Scatter(x=bw_range, y=p_p, name='Sugerido', line=dict(color='#1A5276', width=2.5)))
    fig.add_trace(go.Scatter(x=bw_range, y=p_t, name='Techo Máx.', line=dict(color='#A93226', width=1, dash='dot')))
    fig.add_trace(go.Scatter(x=bw_range, y=p_s, name='Suelo Mín.', line=dict(color='#1E8449', width=1, dash='dot')))

    # 3. Datos de Clientes (Hover estilizado)
    fig.add_trace(go.Scatter(
        x=df['bw'],
        y=df['price'],
        mode='markers',
        name='Portafolio Actual',
        marker=dict(
            size=df['n_clients'],
            sizemode='area',
            sizeref=2. * max(df['n_clients']) / (factor_circulo**2),
            color='#1A5276',
            line=dict(width=0.8, color='white'),
            opacity=0.85
        ),
        # Hover con contraste reducido y tipografía limpia
        text=[f"<b>PLAN: {b} Mbps</b><br>Clientes: {int(c)}<br>Precio: ${p}/Mbps" 
              for c, b, p in zip(df['n_clients'], df['bw'], df['price'])],
        hoverinfo='text'
    ))

    # --- DISEÑO DE INTERFAZ (LAYOUT GUMER) ---
    fig.update_layout(
        title={
            'text': f"<b>{titulo_input.upper()}</b>",
            'y': 0.94,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 22, 'family': 'Arial Black', 'color': '#2C3E50'}
        },
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        height=750,
        margin=dict(l=70, r=50, b=80, t=120),
        
        # LEYENDA TIPO CUADRO PROFESIONAL (Contraste suavizado)
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.98,
            xanchor="right",
            x=0.98,
            bgcolor="rgba(255, 255, 255, 0.85)", # Fondo sutilmente traslúcido
            bordercolor="#D5DBDB", # Gris claro en lugar de negro
            borderwidth=1,
            font=dict(size=11, family='Arial', color='#2C3E50')
        ),
        
        # ETIQUETAS DE HOVER (Contraste suavizado)
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            font_size=13,
            font_family="Arial",
            bordercolor="#D5DBDB"
        )
    )

    # Configuración de Ejes (Alineación 0,0)
    fig.update_xaxes(
        type="log", 
        title="Capacidad contratada (Mbps)", 
        title_font=dict(size=12, family='Arial Bold'),
        range=[0, np.log10(x_max)],
        zeroline=True, zerolinecolor='#2C3E50', linewidth=1.2, 
        gridcolor='#F2F4F4', tickfont=dict(size=10)
    )
    fig.update_yaxes(
        title="Precio Unitario (USD / Mbps)", 
        title_font=dict(size=12, family='Arial Bold'),
        range=[0, y_max],
        zeroline=True, zerolinecolor='#2C3E50', linewidth=1.2, 
        gridcolor='#F2F4F4', tickfont=dict(size=10)
    )

    st.plotly_chart(fig, use_container_width=True, theme=None)

except Exception as e:
    st.info("💡 Pega tus datos de Excel para activar el análisis de portafolio v4.3")

st.sidebar.markdown("---")
st.sidebar.caption("🛡️ Gumersinda Engine v4.3 | By Luis Duque")
