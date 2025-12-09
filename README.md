# Analyse exploratoire du Bitcoin (2012–2025)

Analyse temporelle détaillée des données historiques du Bitcoin (OHLCV à la minute) de janvier 2012 à novembre 2025.

Projet réalisé dans le cadre du cours **8PRO408 – Outils de programmation pour la science des données** à l’UQAC.

---

## Sommaire

- [Objectifs](#-objectifs)
- [Jeu de données](#-jeu-de-données)
- [Installation rapide](#-installation-rapide)
- [Préparation des données](#-préparation-des-données)
- [Utilisation](#-utilisation)
- [Visualisations clés](#-visualisations-clés)
- [Structure du dépôt](#-structure-du-dépôt)
- [Aller plus loin](#-aller-plus-loin)

---

## 🎯 Objectifs

- Explorer l’évolution du prix du Bitcoin sur ~14 ans (2012–2025).
- Étudier la volatilité à différentes échelles temporelles (intra-jour, mensuelle, annuelle).
- Analyser les volumes échangés et leurs liens avec les mouvements de prix.
- Mettre en place une mini-application d’exploration interactive des données avec Streamlit.

---

## 🗂️ Jeu de données

- Source : [Kaggle – BTCUSD Minute Data (2012-2025)](https://www.kaggle.com/datasets/mczielinski/bitcoin-historical-data) ou toute source équivalente fournissant les colonnes `Timestamp`, `Open`, `High`, `Low`, `Close`, `Volume`.
- Couverture temporelle : du 1er janvier 2012 au 26 novembre 2025 (agrégation journalière côté application).
- Fréquence native : 1 minute (OHLCV). Les agrégations journalières et les indicateurs (MA 50/200, volatilité 30 j) sont calculés automatiquement.
- Format : CSV, séparateur virgule, horodatage Unix (secondes). Le fichier `.csv` brut pèse ~1,5 Go.

> 💡 Le dossier `data/` n’est volontairement **pas versionné** pour éviter de stocker des fichiers volumineux. Pensez à l’ajouter à votre `.gitignore` si vous forkez le projet.

---

## ⚙️ Installation rapide

1. **Cloner** le dépôt et créer un environnement virtuel :
   ```bash
   git clone https://github.com/<utilisateur>/bitcoin-analysis.git
   cd bitcoin-analysis
   python -m venv .venv
   source .venv/bin/activate  # sous Windows : .venv\Scripts\activate
   ```
2. **Installer** les dépendances :
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## 📥 Préparation des données

1. Télécharger `btcusd_1-min_data.csv` depuis la source mentionnée plus haut.
2. Placer le fichier dans `data/` (créer le dossier si nécessaire).
3. Optionnel : convertir les timestamps en datetime pour gagner du temps lors de l’exploration dans un notebook.

```bash
mkdir -p data
cp /chemin/vers/btcusd_1-min_data.csv data/
```

Le notebook et l’application Streamlit recherchent automatiquement les données relatives au chemin `data/btcusd_1-min_data.csv`.

---

## 🚀 Utilisation

### 1. Notebook d’analyse

- Lancer Jupyter : `jupyter notebook notebooks/bitcoin_analysis.ipynb`
- Le notebook couvre : nettoyage des données, agrégations temporelles, calculs des indicateurs de momentum, corrélations volume/prix et génération des figures présentes dans `reports/`.

### 2. Application Streamlit

```bash
streamlit run app/streamlit_app.py
```

Fonctionnalités principales :

- Sélecteur de plage de dates (zoom annuel/mensuel/journalier).
- Visualisation du prix avec moyennes mobiles 50/200 jours.
- Graphique en chandelier, histogramme des volumes, volatilité glissante 30 jours.
- Tableau de statistiques synthétiques (prix et rendements).

> ℹ️ L’application attend que le dataset soit accessible sous `../data/btcusd_1-min_data.csv` (chemin relatif au dossier `app/`). Adaptez le chemin si vous exécutez le script depuis un autre répertoire.

---

## 📊 Visualisations clés

Les figures exportées dans `reports/` permettent de documenter l’analyse :

- `price_evolution.png` – trajectoire du prix journalier + moyennes mobiles longue/courte.
- `volatility_analysis.png` – volatilité annuelle (boîtes à moustaches) et volatilité glissante.
- `correlation_heatmap.png` – corrélations entre rendements agrégés, volumes et volatilité.
- `rapport_analyse_bitcoin.pdf` – synthèse écrite (méthodologie, observations, limites).

Ces sorties sont utiles pour partager des résultats statiques sans lancer l’application.

---

## 🧱 Structure du dépôt

```
bitcoin-analysis/
├── data/                       
│   └── btcusd_1-min_data.csv        # À télécharger (non inclus)
│
├── notebooks/                      
│   └── bitcoin_analysis.ipynb       # Notebook Jupyter d'analyse
│
├── app/                            
│   └── streamlit_app.py             # Application Streamlit
│
├── reports/                         
│   ├── rapport_analyse_bitcoin.pdf  # Rapport PDF
│   ├── price_evolution.png
│   ├── volatility_analysis.png
│   └── correlation_heatmap.png
│
├── requirements.txt                 # Dépendances Python
└── README.md                        # Documentation du projet
```

---

## ➕ Aller plus loin

- Tester d’autres granularités (hebdomadaire, horaire) ou activer un échantillonnage adaptatif pour accélérer les calculs.
- Enrichir l’appli Streamlit avec des indicateurs on-chain, un mode comparaison multi-actifs ou des alertes personnalisées.
- Déployer l’app sur Streamlit Community Cloud / Hugging Face Spaces pour simplifier le partage.
