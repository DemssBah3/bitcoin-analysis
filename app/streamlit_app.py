from datetime import date, timedelta
from pathlib import Path
from typing import Sequence, Tuple

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DATA_FILE = DATA_DIR / "btcusd_1-min_data.csv"
SHORT_MA_WINDOW = 50
LONG_MA_WINDOW = 200
VOLATILITY_WINDOW = 30
CANDLE_SAMPLE_LIMIT = 500


def configure_page() -> None:
    """Configure les paramètres de rendu de la page Streamlit."""
    st.set_page_config(
        page_title="Analyse Bitcoin",
        page_icon="₿",
        layout="wide",
        initial_sidebar_state="expanded",
    )


@st.cache_data(show_spinner=False)
def load_data(path: Path = DATA_FILE) -> pd.DataFrame:
    """
    Charge les données OHLCV brutes puis calcule les agrégations quotidiennes.

    Parameters
    ----------
    path : Path
        Chemin vers le fichier CSV contenant les observations à la minute.
    """
    if not path.exists():
        raise FileNotFoundError(
            f"Impossible de trouver le fichier de données : {path}"
        )

    df = pd.read_csv(path)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="s")
    df.set_index("Timestamp", inplace=True)

    # Agrégation journalière
    df_daily = (
        df.resample("D")
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

    # Calculs supplémentaires
    df_daily["Daily_Return"] = df_daily["Close"].pct_change() * 100
    df_daily["MA_50"] = df_daily["Close"].rolling(window=SHORT_MA_WINDOW).mean()
    df_daily["MA_200"] = df_daily["Close"].rolling(window=LONG_MA_WINDOW).mean()
    df_daily["Volatility"] = (
        df_daily["Daily_Return"].rolling(window=VOLATILITY_WINDOW).std()
    )
    df_daily["Range"] = df_daily["High"] - df_daily["Low"]

    return df_daily


def filter_dataframe(
    df_daily: pd.DataFrame, selected_range: Sequence[date] | None
) -> pd.DataFrame:
    """Retourne la portion de dataframe correspondant à l'intervalle choisi."""
    if not selected_range or len(selected_range) != 2:
        return df_daily.copy()

    mask = (
        (df_daily["Date"].dt.date >= selected_range[0])
        & (df_daily["Date"].dt.date <= selected_range[1])
    )
    return df_daily.loc[mask].copy()


def render_metrics(df_filtered: pd.DataFrame) -> None:
    """Affiche les métriques principales du segment visible."""
    st.header("📈 Métriques clés")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        current_price = df_filtered["Close"].iloc[-1]
        st.metric(
            "Prix actuel",
            f"${current_price:,.2f}",
            delta=f"{df_filtered['Daily_Return'].iloc[-1]:.2f}%",
        )

    with col2:
        st.metric("Prix maximum", f"${df_filtered['High'].max():,.2f}")

    with col3:
        st.metric("Prix minimum", f"${df_filtered['Low'].min():,.2f}")

    with col4:
        total_return = (
            (df_filtered["Close"].iloc[-1] - df_filtered["Close"].iloc[0])
            / df_filtered["Close"].iloc[0]
        ) * 100
        st.metric("Variation totale", f"{total_return:,.2f}%")

    with col5:
        st.metric("Volume moyen", f"{df_filtered['Volume'].mean():,.0f} BTC")

    st.markdown("---")


def render_price_chart(df_filtered: pd.DataFrame, show_ma: bool) -> None:
    """Affiche le prix du Bitcoin et les moyennes mobiles configurables."""
    st.header("📉 Évolution du prix du Bitcoin")
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_filtered["Date"],
            y=df_filtered["Close"],
            mode="lines",
            name="Prix de clôture",
            line=dict(color="#1f77b4", width=2),
            fill="tozeroy",
            fillcolor="rgba(31, 119, 180, 0.1)",
        )
    )

    if show_ma:
        fig.add_trace(
            go.Scatter(
                x=df_filtered["Date"],
                y=df_filtered["MA_50"],
                mode="lines",
                name=f"MA {SHORT_MA_WINDOW} jours",
                line=dict(color="orange", width=2, dash="dash"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df_filtered["Date"],
                y=df_filtered["MA_200"],
                mode="lines",
                name=f"MA {LONG_MA_WINDOW} jours",
                line=dict(color="red", width=2, dash="dot"),
            )
        )

    fig.update_layout(
        height=600,
        template="plotly_white",
        hovermode="x unified",
        xaxis_title="Date",
        yaxis_title="Prix (USD)",
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
    )
    st.plotly_chart(fig, use_container_width=True)


def render_candlestick(df_filtered: pd.DataFrame) -> None:
    """Affiche un graphique en chandelier sous-échantillonné pour la performance."""
    st.header("🕯️ Graphique en chandelier")
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
                increasing_line_color="#2ecc71",
                decreasing_line_color="#e74c3c",
            )
        ]
    )
    fig.update_layout(
        height=600,
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Prix (USD)",
        xaxis_rangeslider_visible=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_volume(df_filtered: pd.DataFrame) -> None:
    """Affiche l'histogramme des volumes."""
    st.header("📊 Volume de transactions")
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_filtered["Date"],
            y=df_filtered["Volume"],
            name="Volume",
            marker_color="#ff7f0e",
            opacity=0.7,
        )
    )
    fig.update_layout(
        height=400,
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Volume (BTC)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_volatility(df_filtered: pd.DataFrame) -> None:
    """Affiche la volatilité glissante."""
    st.header(f"🌪️ Volatilité ({VOLATILITY_WINDOW} jours)")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_filtered["Date"],
            y=df_filtered["Volatility"],
            mode="lines",
            name="Volatilité",
            line=dict(color="red", width=2),
            fill="tozeroy",
            fillcolor="rgba(255, 0, 0, 0.2)",
        )
    )
    fig.update_layout(
        height=400,
        template="plotly_white",
        xaxis_title="Date",
        yaxis_title="Volatilité (%)",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_tables(df_filtered: pd.DataFrame) -> None:
    """Affiche les tableaux récapitulatifs prix/rendements."""
    st.markdown("---")
    st.header("📊 Statistiques détaillées")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Prix")
        stats_df = pd.DataFrame(
            {
                "Métrique": ["Prix moyen", "Médiane", "Écart-type", "Min", "Max"],
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
        st.subheader("Rendements")
        returns_df = pd.DataFrame(
            {
                "Métrique": ["Rendement moyen", "Médiane", "Écart-type", "Min", "Max"],
                "Valeur": [
                    f"{df_filtered['Daily_Return'].mean():.3f}%",
                    f"{df_filtered['Daily_Return'].median():.3f}%",
                    f"{df_filtered['Daily_Return'].std():.3f}%",
                    f"{df_filtered['Daily_Return'].min():.3f}%",
                    f"{df_filtered['Daily_Return'].max():.3f}%",
                ],
            }
        )
        st.dataframe(returns_df, hide_index=True, use_container_width=True)


def render_footer() -> None:
    """Affiche un pied de page léger."""
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


def build_sidebar(
    df_daily: pd.DataFrame,
) -> Tuple[Sequence[date] | None, bool, bool]:
    """Configure les filtres et options de la barre latérale."""
    st.sidebar.header("🎛️ Filtres")
    min_date = df_daily["Date"].min().date()
    max_date = df_daily["Date"].max().date()
    default_range = (max_date - timedelta(days=365), max_date)

    date_range = st.sidebar.date_input(
        "📅 Sélectionner la période",
        value=default_range,
        min_value=min_date,
        max_value=max_date,
    )

    st.sidebar.markdown("---")
    st.sidebar.header("📊 Options d'affichage")
    show_ma = st.sidebar.checkbox("Afficher les moyennes mobiles", value=True)
    show_volume = st.sidebar.checkbox("Afficher le volume", value=True)
    return date_range, show_ma, show_volume


def main() -> None:
    """Point d'entrée de l'application Streamlit."""
    configure_page()
    st.title("📊 Analyse Exploratoire du Bitcoin")
    st.markdown("### Données historiques OHLCV (2012-2025)")
    st.markdown("---")

    with st.spinner("🔄 Chargement des données..."):
        try:
            df_daily = load_data()
        except FileNotFoundError as error:
            st.error(
                f"{error}. Vérifiez que le fichier est bien présent dans {DATA_DIR}"
            )
            st.stop()

    date_range, show_ma, show_volume = build_sidebar(df_daily)
    df_filtered = filter_dataframe(df_daily, date_range)

    render_metrics(df_filtered)
    render_price_chart(df_filtered, show_ma)
    render_candlestick(df_filtered)
    if show_volume:
        render_volume(df_filtered)
    render_volatility(df_filtered)
    render_tables(df_filtered)
    render_footer()


if __name__ == "__main__":
    main()
