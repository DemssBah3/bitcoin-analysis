# Analyse Exploratoire du Bitcoin

## Description

Analyse temporelle complète des données historiques du Bitcoin (OHLCV à la minute) de janvier 2012 à novembre 2025.

Ce projet a été réalisé dans le cadre du cours **8PRO408 - Outils de programmation pour la science des données** à l'UQAC.

## 📁 Structure du projet

bitcoin-analysis/ 
├── data/ # Données brutes (CSV) 

├── notebooks/ # Notebook Jupyter d'analyse 
    │ └── bitcoin_analysis.ipynb 

├── app/ # Application Streamlit 
    │ └── streamlit_app.py 

├── reports/ # Rapport PDF et graphiques 
    │ ├── rapport_analyse_bitcoin.pdf 
    │ ├── price_evolution.png │ ├── volatility_analysis.png 
    │ ├── correlation_heatmap.png 
    │ └── ... 
├── requirements.txt # Dépendances Python 

└── README.md # Ce fichier

## 🚀 Installation

### Prérequis
- Python 3.13 ou supérieur
- pip

### Étapes d'installation

1. **Cloner le dépôt**

```bash
git clone https://github.com/DemssBah3/bitcoin-analysis.git
cd bitcoin-analysis

2. **Installer les dépendances**

pip install -r requirements.txt

3. **Télécharger les données**

Téléchargez le dataset depuis Kaggle
Placez le fichier btcusd_1-min_data.csv dans le dossier data/
📊 Utilisation
Notebook Jupyter
Pour explorer l'analyse complète :

Copyjupyter notebook notebooks/bitcoin_analysis.ipynb
Ou avec Python :

Copypython -m notebook notebooks/bitcoin_analysis.ipynb
Application Streamlit
Pour lancer l'application interactive :

Copycd app
python -m streamlit run streamlit_app.py
L'application sera accessible à : http://localhost:8501

📈 Résultats clés
Période analysée : 2012-2025 (~14 ans)
Croissance totale : +1 973 306%
Prix maximum : $126,272
Volatilité moyenne : 3.46% (30 jours)
Meilleure année : 2013 (+5,446%)

🛠️ Technologies utilisées
Python 3.13
pandas - Manipulation de données
NumPy - Calculs numériques
Matplotlib - Visualisations statiques
Seaborn - Visualisations statistiques
Plotly - Visualisations interactives
Streamlit - Application web interactive
Jupyter - Notebooks d'analyse


📄 Livrables
✅ Notebook Jupyter complet avec analyses
✅ Rapport PDF (2 pages)
✅ Application Streamlit fonctionnelle
✅ Graphiques sauvegardés (PNG/HTML)
✅ README documenté


👤 Auteur
Aboubacar Demba Bah, Mamadou Cire Bah, Lahat Fall  
Étudiant(e) - UQAC
Cours : 8PRO408
Date : Décembre 2025

📝 Licence
Ce projet est réalisé à des fins académiques.

🙏 Remerciements
Professeur : HN Doukaga
Dataset : Kaggle (Bitcoin Historical Data)
UQAC - Département d'informatique et de mathématique
