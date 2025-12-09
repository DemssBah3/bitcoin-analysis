# Analyse exploratoire du Bitcoin (2012–2025)

Analyse temporelle détaillée des données historiques du Bitcoin (OHLCV à la minute) de janvier 2012 à novembre 2025.

Projet réalisé dans le cadre du cours **8PRO408 – Outils de programmation pour la science des données** à l’UQAC.

---

## 🎯 Objectifs

- Explorer l’évolution du prix du Bitcoin sur ~14 ans (2012–2025).
- Étudier la volatilité à différentes échelles temporelles (intra-jour, mensuelle, annuelle).
- Analyser les volumes échangés et leurs liens avec les mouvements de prix.
- Mettre en place une mini-application d’exploration interactive des données avec Streamlit.

---

## 📁 Structure du projet

```text
bitcoin-analysis/
|-- data/                     # Données brutes (CSV)
|   `-- btcusd_1-min_data.csv (à télécharger)
|-- notebooks/                # Notebook Jupyter d'analyse
|   `-- bitcoin_analysis.ipynb
|-- app/                      # Application Streamlit
|   `-- streamlit_app.py
|-- reports/                  # Rapport PDF et graphiques exportés
|   |-- rapport_analyse_bitcoin.pdf
|   |-- price_evolution.png
|   |-- volatility_analysis.png
|   `-- correlation_heatmap.png
|-- requirements.txt          # Dépendances Python
`-- README.md                 # Ce fichier
