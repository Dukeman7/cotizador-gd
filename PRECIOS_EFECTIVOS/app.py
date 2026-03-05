import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from io import StringIO
import re

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="IUFO Precision Engine", layout="wide")

# --- BARRA LATERAL (EL CENTRO DE MANDO) ---
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

st.sidebar.subheader("📊 Ajustes de Gráfica")
x_max = st.sidebar.number_input("Máximo X (Mbps)", value=40000)
y_max = st.sidebar.number_input("Máximo Y ($/Mbps)", value=60)

# NUEVO: Control de radio de los círculos
factor_circulo = st.sidebar.slider("Tamaño de los Círculos", 1, 100, 30, help="Desliza para achicar los balones de playa")

# --- CUERPO PRINCIPAL ---
st.title(titulo_input)

st.subheader("📝 Datos del Portafolio")
st.caption("Tip: Pega tus celdas de Excel aquí. El sistema limpia tabuladores y espacios solo.")
raw_data = st.text_area("Formato: Mbps  Precio  Clientes", 
                        value="100  15.0  1\n1000  3.5  12\n10000  1.3  4", height=150)

def calc_curvas(bw):
    L = k_log + np.log10(bw / q)
    p_prom = (A / np.power(bw, n)) + C - L
    p_techo = p_prom + C_sup - (k_sup * L)
    p_suelo = p_prom - C_inf + (k_inf * L)
    return p_prom, p_techo, p_suelo

try:
    # Procesamiento inteligente de datos
    clean_data = re.sub(r'[ \t]+', ',', raw_data.strip())
    df = pd.read_csv(StringIO(clean_data), names=['bw', 'price', 'n_clients'])
    
    # Generar Curvas
    bw_range = np.logspace(0, np.log10(x_max), 500)
    p_p, p_t, p_s = calc_curvas(bw_range)

    # --- CREAR GRÁFICA INTERACTIVA ---
    fig = go.Figure()

    # 1. Banda de Negociación (Sombreado)
    fig.add_trace(go.Scatter(
        x=np.concatenate([bw_range, bw_range[::-1]]),
        y=np.concatenate([p_t, p_s[::-1]]),
        fill='toself',
        fillcolor='rgba(0, 68, 136, 0.08)',
        line=dict(color='rgba(255,255,255,0)'),
        hoverinfo='skip',
        name='Banda de Negociación'
    ))

    # 2. Curvas de Referencia
    fig.add_trace(go.Scatter(x=bw_range, y=p_p, name='Precio Sugerido', line=dict(color='#004488', width=2.5)))
    fig.add_trace(go.Scatter(x=bw_range, y=p_t, name='Límite Techo', line=dict(color='#CC0000', width=1, dash='dash')))
    fig.add_trace(go.Scatter(x=bw_range, y=p_s, name='Límite Suelo', line=dict(color='#008800', width=1, dash='dash')))

    # 3. Puntos de Clientes (CON HOVER Y ESCALA AJUSTABLE)
    fig.add_trace(go.Scatter(
        x=df['bw'],
        y=df['price'],
        mode='markers',
        name='Clientes en el plan',
        marker=dict(
            # Aquí aplicamos el factor de escala que pediste
            size=df['n_clients'],
            sizemode='area',
            sizeref=2. * max(df['n_clients']) / (factor_circulo**2),
            color='#004488',
            line=dict(width=1, color='white')
        ),
        text=[f"<b>Plan: {b} Mbps</b><br>Clientes: {int(c)}<br>Precio: ${p}/Mbps" 
              for c, b, p in zip(df['n_clients'], df['bw'], df['price'])],
        hoverinfo='text'
    ))

    # --- CONFIGURACIÓN ESTRICTA DE EJES (Origen 0,0) ---
    fig.update_xaxes(
        type="log", 
        title="Capacidad contratada (Mbps)", 
        range=[0, np.log10(x_max)], # De 10^0=1 hasta x_max
        gridcolor='rgba(0,0,0,0.05)',
        zeroline=True,
        zerolinecolor='black',
        linewidth=2
    )
    fig.update_yaxes(
        title="Precio Unitario (USD / Mbps)", 
        range=[0, y_max], # Origen estricto en 0
        gridcolor='rgba(0,0,0,0.05)',
        zeroline=True,
        zerolinecolor='black',
        linewidth=2
    )

    fig.update_layout(
        template='plotly_white',
        height=750,
        margin=dict(l=50, r=50, b=50, t=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
    )
# --- CONFIGURACIÓN DE LAYOUT (Fondo blanco y Tooltips visibles) ---
    fig.update_layout(
        template='plotly_white', # Fuerza el tema claro de Plotly
        paper_bgcolor='white',   # Fondo del papel (fuera del eje) en blanco
        plot_bgcolor='white',    # Fondo del área de trazado en blanco
        height=750,
        margin=dict(l=50, r=50, b=50, t=50),
        legend=dict(
            orientation="h", 
            yanchor="bottom", 
            y=1.02, 
            xanchor="right", 
            x=1,
            font=dict(color="black") # Asegura leyendas negras
        ),
        # Esto es lo que arregla tus tooltips:
        hoverlabel=dict(
            bgcolor="white", 
            font_size=13, 
            font_family="Arial",
            font_color="black",      # Forzamos texto negro en el tooltip
            bordercolor="#004488"    # Un borde elegante azul para que resalte
        ),
        hovermode="closest"
    )

    # Para evitar que Streamlit sobrescriba el tema, usamos theme=None
    st.plotly_chart(fig, use_container_width=True, theme=None)
# Botón para descargar como HTML (Mantiene la interactividad)
    st.download_button(
        label="💾 Descargar Gráfica Interactiva",
        data=fig.to_html(),
        file_name="matriz_tarificacion.html",
        mime="text/html",
except Exception as e:
    st.info("Pega tus datos arriba para ver la magia. Formato: Mbps [Tab] Precio [Tab] Cantidad")

st.sidebar.markdown("---")
st.sidebar.caption("Desarrollo: Ing. Luis Duque | Modo Gumersinda v4.1")
