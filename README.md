# Analyse exploratoire du Bitcoin

## Apercu
- Analyse temporelle des donnees historiques du Bitcoin (OHLCV a la minute) de janvier 2012 a novembre 2025.
- Projet realise dans le cadre du cours **8PRO408 - Outils de programmation pour la science des donnees** a l'UQAC.

## Structure du projet
```
bitcoin-analysis-main/
|-- data/                 # Donnees brutes (CSV)
|-- notebooks/            # Notebook Jupyter d'analyse
|   `-- bitcoin_analysis.ipynb
|-- app/                  # Application Streamlit
|   `-- streamlit_app.py
|-- reports/              # Rapport PDF et graphiques exportes
|   |-- rapport_analyse_bitcoin.pdf
|   |-- price_evolution.png
|   |-- volatility_analysis.png
|   `-- correlation_heatmap.png
|-- requirements.txt      # Dependances Python
`-- README.md             # Ce fichier
```

## Prerequis
- Python 3.13 ou superieur
- pip

## Installation
1. Cloner le depot :
   ```bash
git clone https://github.com/DemssBah3/bitcoin-analysis.git
cd bitcoin-analysis
   ```
2. (Optionnel) Creer et activer un environnement virtuel :
   ```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate
   ```
3. Installer les dependances :
   ```bash
pip install -r requirements.txt
   ```

## Donnees (a telecharger)
- Le fichier `btcusd_1-min_data.csv` (~365 MB) n'est pas inclus pour des raisons de taille.
- Source : [Kaggle - Bitcoin Historical Data](https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data).
- Apres telechargement, placez le fichier dans `data/`.

## Utilisation
- Notebook Jupyter :
  ```bash
jupyter notebook notebooks/bitcoin_analysis.ipynb
  ```
- Application Streamlit :
  ```bash
cd app
streamlit run streamlit_app.py
  ```
  L'application sera accessible sur http://localhost:8501.

## Resultats cles
- Periode analysee : 2012-2025 (~14 ans)
- Croissance totale : +1 973 306%
- Prix maximum : 126 272 $
- Volatilite moyenne (30 jours) : 3.46%
- Meilleure annee : 2013 (+5 446%)

## Technologies
- Python 3.13, pandas, NumPy, Matplotlib, Seaborn, Plotly, Streamlit, Jupyter

## Livrables
- Notebook Jupyter complet
- Rapport PDF (2 pages)
- Application Streamlit fonctionnelle
- Graphiques exportes (PNG/HTML)

## Auteurs
Aboubacar Demba Bah, Mamadou Cire Bah, Lahat Fall  
Etudiant(e) - UQAC | Cours : 8PRO408 | Date : decembre 2025

## Licence
Projet realise a des fins academiques.

## Remerciements
- Professeur : HN Doukaga
- Dataset : Kaggle (Bitcoin Historical Data)
- UQAC - Departement d'informatique et de mathematique
