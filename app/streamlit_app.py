from datetime import date, timedelta
from pathlib import Path
from typing import Sequence, Tuple

import os
import gdown
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# =========================
# CONFIG FICHIERS & TÉLÉCHARGEMENT
# =========================

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_FILE = DATA_DIR / "btcusd_1-min_data.csv"

# Télécharger le fichier depuis Google Drive si nécessaire
if not DATA_FILE.exists():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_id = "1hQPfQHlsB5w2LF6wvX-pvymLHtPPIObC"
    url = f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
    gdown.download(url, str(DATA_FILE), quiet=False, fuzzy=True)

# Vérifier que le fichier n'est pas une page HTML
if DATA_FILE.exists():
    with open(DATA_FILE, "r") as f:
        first_line = f.readline()
        if "<" in first_line or "html" in first_line.lower():
            os.remove(DATA_FILE)
            raise Exception(
                "Le téléchargement a échoué. Google Drive a renvoyé une page HTML."
            )

# =========================
# PARAMÈTRES GLOBAUX
# =========================

AGGREGATION_OPTIONS = {
    "Horaire": "H",
    "Journalière": "D",
    "Mensuelle": "M",
}

MA_WINDOWS = {
    "H": (24, 24 * 7),  # 1 jour / 1 semaine
    "D": (50, 200),     # MA50 / MA200
    "M": (6, 24),       # 6 / 24 mois
}

VOLATILITY_WINDOWS = {
    "H": 24,   # 24 heures
    "D": 30,   # 30 jours
    "M": 12,   # 12 mois
}

DEFAULT_RANGE_DAYS = 365

RETURN_COL = "Return_pct"
VOLATILITY_COL = "Volatility_pct"
MA_SHORT_COL = "MA_short"
MA_LONG_COL = "MA_long"

CANDLE_SAMPLE_LIMIT = 500

CUSTOM_CSS = """
<style>
:root {
    --primary-bg: linear-gradient(135deg, #0f172a 0%, #1e293b 45%, #020617 100%);
    --card-bg: rgba(15, 23, 42, 0.95);
    --text-primary: #e2e8f0;
}

body {
    background-color: #020617;
}

div.block-container {
    padding: 2.5rem 4rem 3rem;
    background: transparent;
    color: var(--text-primary);
}

.stApp {
    background: var(--primary-bg);
}

.metric-card {
    background: var(--card-bg);
    border-radius: 18px;
    padding: 1.1rem 1.5rem 1.4rem;
    box-shadow: 0 30px 40px rgba(2, 6, 23, 0.45);
    margin-bottom: 1.5rem;
    border: 1px solid rgba(148, 163, 184, 0.2);
}

.metric-card-label {
    font-size: 0.9rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

.metric-card-value {
    color: #f1f5f9;
    font-size: 1.9rem;
    font-weight: 700;
    margin-top: 0.2rem;
}

.metric-delta {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-weight: 600;
    margin-top: 0.5rem;
    font-size: 0.95rem;
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
    color: #0f172a;
}

.metric-delta.positive {
    background: rgba(74, 222, 128, 0.8);
}

.metric-delta.negative {
    background: rgba(252, 165, 165, 0.8);
}

section.main div.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    color: #cbd5f5;
    border-radius: 999px;
}

section.main div.stTabs [aria-selected="true"] {
    background-color: rgba(148, 163, 184, 0.25);
    color: #ffffff;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary);
}

.css-zt5igj, .css-10trblm {
    color: var(--text-primary);
}
</style>
"""

# =========================
# CONFIG STREAMLIT
# =========================

def configure_page() -> None:
    st.set_page_config(
        page_title="Analyse Bitcoin",
        page_icon="₿",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def inject_custom_style() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# =========================
# UTILITAIRES DE PARAMÈTRES
# =========================

def get_ma_windows(freq: str) -> Tuple[int, int]:
    return MA_WINDOWS.get(freq, MA_WINDOWS["D"])


def get_volatility_window(freq: str) -> int:
    return VOLATILITY_WINDOWS.get(freq, VOLATILITY_WINDOWS["D"])


def render_metric_card(label: str, value: str, delta: float | None = None) -> None:
    delta_html = ""
    if delta is not None:
        direction = "positive" if delta >= 0 else "negative"
        arrow = "▲" if delta >= 0 else "▼"
        delta_html = (
            f'<div class="metric-delta {direction}">{arrow}&nbsp;{delta:.2f}%</div>'
        )

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-card-label">{label}</div>
            <div class="metric-card-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# CHARGEMENT & AGRÉGATION
# =========================

@st.cache_data(show_spinner=False)
def load_raw_data(path: Path = DATA_FILE) -> pd.DataFrame:
    """
    Charge les données OHLCV brutes (minute) depuis le CSV.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Impossible de trouver le fichier de données : {path}"
        )

    df = pd.read_csv(
        path,
        usecols=["Timestamp", "Open", "High", "Low", "Close", "Volume"],
    )
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s")
    df.sort_values("Timestamp", inplace=True)
    df.set_index("Timestamp", inplace=True)
    return df


@st.cache_data(show_spinner=False)
def get_aggregated_data(freq: str) -> pd.DataFrame:
    """
    Agrège les données selon la fréquence souhaitée (H, D, M)
    et calcule les indicateurs dérivés.
    """
    df = load_raw_data()
    aggregated = (
        df.resample(freq)
        .agg(
            {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
                "Volume": "sum",
            }
        )
        .dropna()
        .reset_index()
        .rename(columns={"Timestamp": "Date"})
    )

    aggregated["Date"] = pd.to_datetime(aggregated["Date"])
    aggregated[RETURN_COL] = aggregated["Close"].pct_change() * 100

    short_window, long_window = get_ma_windows(freq)
    aggregated[MA_SHORT_COL] = aggregated["Close"].rolling(short_window).mean()
    aggregated[MA_LONG_COL] = aggregated["Close"].rolling(long_window).mean()

    aggregated[VOLATILITY_COL] = (
        aggregated[RETURN_COL].rolling(get_volatility_window(freq)).std()
    )

    aggregated["Range"] = aggregated["High"] - aggregated["Low"]
    return aggregated


@st.cache_data(show_spinner=False)
def get_time_bounds(path: Path = DATA_FILE) -> Tuple[date, date]:
    df = load_raw_data(path)
    return df.index.min().date(), df.index.max().date()


def filter_dataframe(
    df_view: pd.DataFrame, selected_range: Sequence[date] | None
) -> pd.DataFrame:
    if not selected_range or len(selected_range) != 2:
        return df_view.copy()

    mask = (
        (df_view["Date"].dt.date >= selected_range[0])
        & (df_view["Date"].dt.date <= selected_range[1])
    )
    return df_view.loc[mask].copy()


# =========================
# RENDU DES MÉTRIQUES & GRAPHIQUES
# =========================

def render_metrics(df_filtered: pd.DataFrame) -> None:
    st.header("📈 Métriques clés")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        current_price = df_filtered["Close"].iloc[-1]
        delta = df_filtered[RETURN_COL].iloc[-1]
        render_metric_card("Prix actuel", f"${current_price:,.2f}", delta)

    with col2:
        render_metric_card("Prix maximum", f"${df_filtered['High'].max():,.2f}")

    with col3:
        render_metric_card("Prix minimum", f"${df_filtered['Low'].min():,.2f}")

    with col4:
        if len(df_filtered) > 1:
            total_return = (
                (df_filtered["Close"].iloc[-1] - df_filtered["Close"].iloc[0])
                / df_filtered["Close"].iloc[0]
            ) * 100
        else:
            total_return = 0.0
        render_metric_card("Variation totale", f"{total_return:,.2f}%")

    with col5:
        render_metric_card("Volume moyen", f"{df_filtered['Volume'].mean():,.0f} BTC")

    st.markdown("---")


def render_price_chart(
    df_filtered: pd.DataFrame, show_ma: bool, freq: str
) -> None:
    st.header("📉 Évolution du prix du Bitcoin")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_filtered["Date"],
            y=df_filtered["Close"],
            mode="lines",
            name="Prix de clôture",
            line=dict(color="#38bdf8", width=2),
            fill="tozeroy",
            fillcolor="rgba(56, 189, 248, 0.1)",
        )
    )

    if show_ma:
        short_window, long_window = get_ma_windows(freq)
        fig.add_trace(
            go.Scatter(
                x=df_filtered["Date"],
                y=df_filtered[MA_SHORT_COL],
                mode="lines",
                name=f"MA courte ({short_window} périodes)",
                line=dict(color="#facc15", width=2, dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_filtered["Date"],
                y=df_filtered[MA_LONG_COL],
                mode="lines",
                name=f"MA longue ({long_window} périodes)",
                line=dict(color="#f97316", width=2, dash="dot"),
            )
        )

    fig.update_layout(
        height=600,
        template="plotly_dark",
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Prix (USD)",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(2, 6, 23, 0.7)",
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_candlestick(df_filtered: pd.DataFrame) -> None:
    st.header("🕯 Graphique en chandelier")
    step = max(1, len(df_filtered) // CANDLE_SAMPLE_LIMIT)
    df_candle = df_filtered.iloc[::step]

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df_candle["Date"],
                open=df_candle["Open"],
                high=df_candle["High"],
                low=df_candle["Low"],
                close=df_candle["Close"],
                increasing_line_color="#22c55e",
                decreasing_line_color="#ef4444",
            )
        ]
    )
    fig.update_layout(
        height=600,
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Prix (USD)",
        xaxis_rangeslider_visible=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_volume(df_filtered: pd.DataFrame) -> None:
    st.header("📊 Volume de transactions")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_filtered["Date"],
            y=df_filtered["Volume"],
            name="Volume",
            marker_color="#f97316",
            opacity=0.85,
        )
    )
    fig.update_layout(
        height=400,
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Volume (BTC)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_price_volume_relation(df_filtered: pd.DataFrame) -> None:
    st.header("🔁 Relation prix / volume")
    fig = go.Figure(
        data=[
            go.Scatter(
                x=df_filtered["Volume"],
                y=df_filtered["Close"],
                mode="markers",
                marker=dict(
                    size=8,
                    color=df_filtered[RETURN_COL],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Variation (%)"),
                    opacity=0.85,
                ),
                text=df_filtered["Date"].dt.strftime("%Y-%m-%d %H:%M"),
                hovertemplate=(
                    "Date : %{text}<br>Volume : %{x:,.0f} BTC"
                    "<br>Prix : $%{y:,.2f}<br>Variation : %{marker.color:.2f}%"
                ),
            )
        ]
    )
    fig.update_layout(
        height=450,
        template="plotly_dark",
        xaxis_title="Volume (BTC)",
        yaxis_title="Prix (USD)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_volatility(df_filtered: pd.DataFrame, freq: str) -> None:
    window = get_volatility_window(freq)
    st.header(f"🌪 Volatilité glissante ({window} périodes)")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_filtered["Date"],
            y=df_filtered[VOLATILITY_COL],
            mode="lines",
            name="Volatilité",
            line=dict(color="#f87171", width=2),
            fill="tozeroy",
            fillcolor="rgba(248, 113, 113, 0.25)",
        )
    )
    fig.update_layout(
        height=400,
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Volatilité (%)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_correlation_heatmap(df_filtered: pd.DataFrame) -> None:
    st.header("🔥 Corrélations simples")
    corr = df_filtered[
        ["Close", "Volume", RETURN_COL, VOLATILITY_COL, "Range"]
    ].corr()
    fig = go.Figure(
        data=[
            go.Heatmap(
                z=corr.values,
                x=corr.columns,
                y=corr.columns,
                colorscale="RdBu",
                reversescale=True,
                text=corr.round(2).values,
                texttemplate="%{text}",
                hovertemplate="Corr(%{y}, %{x}) = %{z:.2f}<extra></extra>",
            )
        ]
    )
    fig.update_layout(height=500, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)


def render_tables(df_filtered: pd.DataFrame) -> None:
    st.markdown("---")
    st.header("📊 Statistiques détaillées")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Prix")
        stats_df = pd.DataFrame(
            {
                "Métrique": ["Moyenne", "Médiane", "Écart-type", "Min", "Max"],
                "Valeur": [
                    f"${df_filtered['Close'].mean():,.2f}",
                    f"${df_filtered['Close'].median():,.2f}",
                    f"${df_filtered['Close'].std():,.2f}",
                    f"${df_filtered['Close'].min():,.2f}",
                    f"${df_filtered['Close'].max():,.2f}",
                ],
            }
        )
        st.dataframe(stats_df, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Variations (%)")
        returns_df = pd.DataFrame(
            {
                "Métrique": ["Moyenne", "Médiane", "Écart-type", "Min", "Max"],
                "Valeur": [
                    f"{df_filtered[RETURN_COL].mean():.3f}%",
                    f"{df_filtered[RETURN_COL].median():.3f}%",
                    f"{df_filtered[RETURN_COL].std():.3f}%",
                    f"{df_filtered[RETURN_COL].min():.3f}%",
                    f"{df_filtered[RETURN_COL].max():.3f}%",
                ],
            }
        )
        st.dataframe(returns_df, hide_index=True, use_container_width=True)


def render_footer() -> None:
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>📊 Analyse réalisée dans le cadre du cours 8PRO408</p>
            <p>🎓 UQAC - Décembre 2025</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# SIDEBAR & MAIN
# =========================

def build_sidebar(
    min_date: date, max_date: date
) -> Tuple[str, Sequence[date], bool, bool]:
    st.sidebar.header("🎛 Filtres")
    freq_label = st.sidebar.radio(
        "Granularité",
        list(AGGREGATION_OPTIONS.keys()),
        index=1,
    )

    default_start = max_date - timedelta(days=DEFAULT_RANGE_DAYS)
    if default_start < min_date:
        default_start = min_date

    date_range = st.sidebar.date_input(
        "📅 Sélectionner la période",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    st.sidebar.markdown("---")
    st.sidebar.header("📊 Options d'affichage")
    show_ma = st.sidebar.checkbox("Moyennes mobiles", value=True)
    show_volume = st.sidebar.checkbox("Histogramme des volumes", value=True)
    return freq_label, date_range, show_ma, show_volume


def main() -> None:
    configure_page()
    inject_custom_style()
    st.title("📊 Analyse Exploratoire du Bitcoin")
    st.markdown("### Données historiques OHLCV (2012-2025)")
    st.markdown("---")

    try:
        min_date, max_date = get_time_bounds()
    except FileNotFoundError as error:
        st.error(f"{error}. Vérifiez que le fichier est bien présent dans {DATA_DIR}")
        st.stop()

    freq_label, date_range, show_ma, show_volume = build_sidebar(min_date, max_date)
    freq = AGGREGATION_OPTIONS[freq_label]

    with st.spinner("🔄 Agrégation des données..."):
        try:
            df_view = get_aggregated_data(freq)
        except FileNotFoundError as error:
            st.error(f"{error}. Vérifiez que le fichier est bien présent dans {DATA_DIR}")
            st.stop()

    df_filtered = filter_dataframe(df_view, date_range)
    if df_filtered.empty:
        st.warning("Aucune donnée pour la période sélectionnée.")
        st.stop()

    render_metrics(df_filtered)

    tab_price, tab_volume, tab_analytics, tab_stats = st.tabs(
        ["📉 Prix & tendance", "📊 Volumes", "🧠 Analyses avancées", "📑 Statistiques"]
    )

    with tab_price:
        render_price_chart(df_filtered, show_ma, freq)
        render_candlestick(df_filtered)

    with tab_volume:
        if show_volume:
            render_volume(df_filtered)
        else:
            st.info(
                "Activez l’option “Histogramme des volumes” dans la barre latérale "
                "pour afficher ce graphique."
            )
        render_price_volume_relation(df_filtered)

    with tab_analytics:
        render_volatility(df_filtered, freq)
        render_correlation_heatmap(df_filtered)

    with tab_stats:
        render_tables(df_filtered)

    render_footer()


if __name__ == "__main__":
    main()
