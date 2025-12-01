import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime, timedelta

# Configuration de la page
st.set_page_config(
    page_title="Analyse Bitcoin",
    page_icon="₿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titre principal
st.title("📊 Analyse Exploratoire du Bitcoin")
st.markdown("### Données historiques OHLCV (2012-2025)")
st.markdown("---")

# Fonction de chargement des données avec cache
@st.cache_data
def load_data():
    """Charge et prépare les données Bitcoin"""
    # Charger les données
    df = pd.read_csv('../data/btcusd_1-min_data.csv')
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], unit='s')
    
    # Agrégation journalière
    df_daily = df.groupby(df['Timestamp'].dt.date).agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).reset_index()
    
    df_daily.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df_daily['Date'] = pd.to_datetime(df_daily['Date'])
    
    # Calculs supplémentaires
    df_daily['Daily_Return'] = df_daily['Close'].pct_change() * 100
    df_daily['MA_50'] = df_daily['Close'].rolling(window=50).mean()
    df_daily['MA_200'] = df_daily['Close'].rolling(window=200).mean()
    df_daily['Volatility'] = df_daily['Daily_Return'].rolling(window=30).std()
    df_daily['Range'] = df_daily['High'] - df_daily['Low']
    
    return df_daily

# Chargement des données
with st.spinner('🔄 Chargement des données...'):
    df_daily = load_data()

# Sidebar - Filtres
st.sidebar.header("🎛️ Filtres")

# Sélection de la période
min_date = df_daily['Date'].min().date()
max_date = df_daily['Date'].max().date()

date_range = st.sidebar.date_input(
    "📅 Sélectionner la période",
    value=(max_date - timedelta(days=365), max_date),
    min_value=min_date,
    max_value=max_date
)

# Filtrer les données
if len(date_range) == 2:
    mask = (df_daily['Date'].dt.date >= date_range[0]) & (df_daily['Date'].dt.date <= date_range[1])
    df_filtered = df_daily[mask].copy()
else:
    df_filtered = df_daily.copy()

# Sidebar - Options d'affichage
st.sidebar.markdown("---")
st.sidebar.header("📊 Options d'affichage")
show_ma = st.sidebar.checkbox("Afficher les moyennes mobiles", value=True)
show_volume = st.sidebar.checkbox("Afficher le volume", value=True)

# Métriques principales
st.header("📈 Métriques clés")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    current_price = df_filtered['Close'].iloc[-1]
    st.metric(
        "Prix actuel",
        f"${current_price:,.2f}",
        delta=f"{df_filtered['Daily_Return'].iloc[-1]:.2f}%"
    )

with col2:
    max_price = df_filtered['High'].max()
    st.metric("Prix maximum", f"${max_price:,.2f}")

with col3:
    min_price = df_filtered['Low'].min()
    st.metric("Prix minimum", f"${min_price:,.2f}")

with col4:
    total_return = ((df_filtered['Close'].iloc[-1] - df_filtered['Close'].iloc[0]) / df_filtered['Close'].iloc[0]) * 100
    st.metric("Variation totale", f"{total_return:,.2f}%")

with col5:
    avg_volume = df_filtered['Volume'].mean()
    st.metric("Volume moyen", f"{avg_volume:,.0f} BTC")

st.markdown("---")

# Graphique 1 : Évolution du prix avec moyennes mobiles
st.header("📉 Évolution du prix du Bitcoin")

fig1 = go.Figure()

# Prix de clôture
fig1.add_trace(go.Scatter(
    x=df_filtered['Date'],
    y=df_filtered['Close'],
    mode='lines',
    name='Prix de clôture',
    line=dict(color='#1f77b4', width=2),
    fill='tozeroy',
    fillcolor='rgba(31, 119, 180, 0.1)'
))

# Moyennes mobiles
if show_ma:
    fig1.add_trace(go.Scatter(
        x=df_filtered['Date'],
        y=df_filtered['MA_50'],
        mode='lines',
        name='MA 50 jours',
        line=dict(color='orange', width=2, dash='dash')
    ))
    
    fig1.add_trace(go.Scatter(
        x=df_filtered['Date'],
        y=df_filtered['MA_200'],
        mode='lines',
        name='MA 200 jours',
        line=dict(color='red', width=2, dash='dot')
    ))

fig1.update_layout(
    height=600,
    template='plotly_white',
    hovermode='x unified',
    xaxis_title='Date',
    yaxis_title='Prix (USD)',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor='rgba(255, 255, 255, 0.8)'
    )
)

st.plotly_chart(fig1, use_container_width=True)

# Graphique 2 : Chandelier
st.header("🕯️ Graphique en chandelier")

# Sous-échantillonner pour la performance
df_candle = df_filtered.iloc[::max(1, len(df_filtered)//500)]

fig2 = go.Figure(data=[go.Candlestick(
    x=df_candle['Date'],
    open=df_candle['Open'],
    high=df_candle['High'],
    low=df_candle['Low'],
    close=df_candle['Close'],
    increasing_line_color='#2ecc71',
    decreasing_line_color='#e74c3c'
)])

fig2.update_layout(
    height=600,
    template='plotly_white',
    xaxis_title='Date',
    yaxis_title='Prix (USD)',
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig2, use_container_width=True)

# Graphique 3 : Volume
if show_volume:
    st.header("📊 Volume de transactions")
    
    fig3 = go.Figure()
    
    fig3.add_trace(go.Bar(
        x=df_filtered['Date'],
        y=df_filtered['Volume'],
        name='Volume',
        marker_color='#ff7f0e',
        opacity=0.7
    ))
    
    fig3.update_layout(
        height=400,
        template='plotly_white',
        xaxis_title='Date',
        yaxis_title='Volume (BTC)',
        showlegend=False
    )
    
    st.plotly_chart(fig3, use_container_width=True)

# Graphique 4 : Volatilité
st.header("🌪️ Volatilité (30 jours)")

fig4 = go.Figure()

fig4.add_trace(go.Scatter(
    x=df_filtered['Date'],
    y=df_filtered['Volatility'],
    mode='lines',
    name='Volatilité',
    line=dict(color='red', width=2),
    fill='tozeroy',
    fillcolor='rgba(255, 0, 0, 0.2)'
))

fig4.update_layout(
    height=400,
    template='plotly_white',
    xaxis_title='Date',
    yaxis_title='Volatilité (%)',
    showlegend=False
)

st.plotly_chart(fig4, use_container_width=True)

# Statistiques détaillées
st.markdown("---")
st.header("📊 Statistiques détaillées")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Prix")
    stats_df = pd.DataFrame({
        'Métrique': ['Prix moyen', 'Médiane', 'Écart-type', 'Min', 'Max'],
        'Valeur': [
            f"${df_filtered['Close'].mean():,.2f}",
            f"${df_filtered['Close'].median():,.2f}",
            f"${df_filtered['Close'].std():,.2f}",
            f"${df_filtered['Close'].min():,.2f}",
            f"${df_filtered['Close'].max():,.2f}"
        ]
    })
    st.dataframe(stats_df, hide_index=True, use_container_width=True)

with col2:
    st.subheader("Rendements")
    returns_df = pd.DataFrame({
        'Métrique': ['Rendement moyen', 'Médiane', 'Écart-type', 'Min', 'Max'],
        'Valeur': [
            f"{df_filtered['Daily_Return'].mean():.3f}%",
            f"{df_filtered['Daily_Return'].median():.3f}%",
            f"{df_filtered['Daily_Return'].std():.3f}%",
            f"{df_filtered['Daily_Return'].min():.3f}%",
            f"{df_filtered['Daily_Return'].max():.3f}%"
        ]
    })
    st.dataframe(returns_df, hide_index=True, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center'>
        <p>📊 Analyse réalisée dans le cadre du cours 8PRO408</p>
        <p>🎓 UQAC - Décembre 2025</p>
    </div>
    """,
    unsafe_allow_html=True
)
