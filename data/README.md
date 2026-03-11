# README — Dossier `data`

## Objectif

Le dossier `data` regroupe l’ensemble du **pipeline de collecte, transformation et préparation des données immobilières** utilisées dans le projet **Observatoire Immobilier Toulon**.

Deux sources principales de données sont utilisées :

- **DVF (Demandes de Valeurs Foncières)** — données officielles des transactions immobilières issues de `data.gouv.fr`
- **SeLoger** — annonces immobilières collectées automatiquement via un workflow **GumLoop**

Ces deux sources permettent de :

- analyser **les prix réels du marché immobilier**
- analyser **les prix affichés dans les annonces**
- construire un dataset exploitable pour **les statistiques, la régression et l'application Streamlit**

---

# Pipeline DVF — Données notariales

## Source des données

Les données DVF proviennent du dataset officiel :

<https://www.data.gouv.fr/fr/datasets/demandes-de-valeurs-foncieres/>

Ce dataset contient **l’ensemble des transactions immobilières enregistrées par les notaires en France**.

Les fichiers bruts sont placés dans :

```
data/raw/
```

Fichiers utilisés :

```
ValeursFoncieres-2023.txt
ValeursFoncieres-2024.txt
ValeursFoncieres-2025-S1.txt
```

Ces fichiers contiennent toutes les transactions immobilières en France.  
Le script `dvf.py` permet d’extraire uniquement les transactions correspondant à **Toulon**.

---

# Script `dvf.py`

## Objectif

Le script `dvf.py` permet de :

1. Lire les fichiers DVF bruts
2. Filtrer uniquement les transactions de la ville de **Toulon**
3. Conserver uniquement certains types de biens
4. Enrichir les données avec des informations géographiques
5. Calculer le **prix au m²**

---

## Filtrage des données

Les transactions sont filtrées selon :

```
Code departement = 83
Code commune = 137
```

Ce filtrage permet de conserver uniquement **les transactions immobilières de Toulon**.

---

## Types de biens conservés

Seuls les biens suivants sont conservés :

```
Maison
Appartement
```

Les autres types de biens (dépendances, terrains, locaux commerciaux, etc.) sont ignorés.

---

# Enrichissement des données

Le script ajoute plusieurs informations utiles pour l’analyse.

## Adresse

Les colonnes DVF suivantes sont combinées :

```
No voie
Type de voie
Voie
```

pour reconstruire une **adresse complète**.

Exemple :

```
12 Rue de la République
```

Une nouvelle colonne est créée :

```
adresse_complete
```

---

## Code postal

La colonne suivante est conservée :

```
Code postal
```

Cette information permet de réaliser des analyses géographiques.

---

## Nombre de pièces

Le dataset DVF contient la colonne :

```
Nombre pieces principales
```

Elle est convertie et stockée dans :

```
nombre_pieces
```

---

## Calcul du prix au m²

Le prix au m² est calculé avec la formule :

```
prix_m2 = valeur_fonciere / surface_reelle_bati
```

Cela permet de comparer les biens indépendamment de leur surface.

---

# Approximation des zones de Toulon

Une colonne supplémentaire est créée :

```
zone_toulon
```

Elle correspond à une **segmentation géographique simplifiée de la ville**.

Correspondance utilisée :

| Code postal | Zone |
|-------------|------|
| 83000 | Centre / Littoral |
| 83100 | Est Toulon |
| 83200 | Ouest Toulon |
| autre | Zone inconnue |

Cette approximation permet d’analyser les prix immobiliers **par zone de la ville**.

---

# Dataset généré

Le script produit le fichier :

```
data/dvf_toulon.csv
```

Structure du dataset :

```
date_mutation
commune
code_postal
zone_toulon

numero_voie
type_voie
voie
adresse_complete

type_local
nombre_pieces

surface_reelle_bati
valeur_fonciere
prix_m2
```

---

# Nettoyage des données — `clean_dvf.py`

Le script `clean_dvf.py` permet de **nettoyer les données DVF** afin d’obtenir un dataset exploitable pour l’analyse.

Le nettoyage inclut :

- suppression des surfaces nulles ou négatives
- suppression des prix incohérents
- suppression des prix au m² aberrants
- vérification des valeurs numériques

Exemples de filtres :

```
surface_reelle_bati > 0
surface entre 10 et 500 m²
prix_m2 entre 500 et 20000
```

Le script produit le fichier :

```
data/dvf_toulon_clean.csv
```

Ce fichier est utilisé pour :

- les statistiques
- la régression
- l’application Streamlit

---

# Architecture du pipeline DVF

```
Fichiers DVF bruts (data.gouv.fr)
        │
        ▼
dvf.py
Extraction + enrichissement
        │
        ▼
dvf_toulon.csv
        │
        ▼
clean_dvf.py
Nettoyage des données
        │
        ▼
dvf_toulon_clean.csv
```

---

# Pipeline SeLoger (GumLoop)

README — Scraping automatisé des annonces SeLoger avec GumLoop

## 1. Objectif du workflow

Ce workflow GumLoop permet de collecter automatiquement des annonces immobilières depuis SeLoger, d'en extraire les informations structurées via un LLM (Gemini), puis de générer deux formats d’export : JSON et CSV.

Le workflow est automatisé et planifié pour s’exécuter chaque lundi à 08:00.

________________

## 2. Déclencheur du workflow

Trigger — Schedule

Objectif  
Lancer automatiquement le workflow sans intervention humaine.

Configuration

| Paramètre | Valeur |
|-----------|-------|
| Type | Schedule Trigger |
| Fréquence | Hebdomadaire |
| Jour | Lundi |
| Heure | 08:00 |

Fonctionnement

Chaque lundi matin à 08h00, le workflow démarre automatiquement et :

1. Génère les URLs des pages SeLoger  
2. Scrape les annonces  
3. Extrait les données avec Gemini  
4. Formate les données  
5. Génère les fichiers JSON et CSV  

________________

## 3. Architecture du workflow

```
Schedule Trigger (Lundi 08:00)
       │
       ▼
Génération URLs pagination
       │
       ▼
Scraping des pages
       │
       ▼
Extraction des annonces (LLM Gemini)
       │
       ▼
Formatage des données
       │
       ├──► Export JSON
       │
       └──► Export CSV
```

________________

## 4. Étapes du workflow

### Node 1 — Génération des URLs SeLoger

Objectif  
Créer automatiquement les URLs des 15 premières pages de résultats SeLoger afin de récupérer plusieurs pages d'annonces.

Exemple de pagination :

```
https://www.seloger.com/list.htm?page=1
https://www.seloger.com/list.htm?page=2
https://www.seloger.com/list.htm?page=3
...
https://www.seloger.com/list.htm?page=15
```

Sortie  
Une liste contenant **15 URLs de pages de résultats**.

________________

### Node 2 — Scraping des pages d'annonces

Objectif  
Récupérer toutes les URLs des annonces immobilières présentes sur les pages générées à l’étape précédente.

Sortie  
Une liste contenant **toutes les URLs des annonces détectées**.

________________

### Node 3 — Extraction des données avec LLM (Gemini)

Objectif  
Analyser le contenu de chaque page d'annonce et extraire toutes les données immobilières structurées.

Principe

1. Le contenu HTML de la page est converti en markdown  
2. Le markdown est envoyé au LLM  
3. Le LLM retourne un JSON structuré  

________________

### Node 4 — Formatage des données

Objectif  
Nettoyer et préparer les données avant l'export.

Transformations possibles :

- validation JSON
- normalisation des champs
- correction des valeurs null
- harmonisation des types numériques
- préparation des colonnes pour export CSV

________________

### Node 5 — Génération du fichier JSON

Objectif  
Créer un fichier JSON complet contenant toutes les annonces extraites.

Format :

```
annonces_seloger.json
```

Structure :

```
[
 {annonce1},
 {annonce2},
 {annonce3}
]
```

________________

### Node 6 — Génération du fichier CSV

Objectif  
Créer un fichier CSV exploitable dans Excel, Google Sheets ou un CRM.

Structure du CSV

```
titre
prix
surface
nb_pieces
nb_chambres
ville
code_postal
adresse
type_bien
lien
description
quartier
```

Chaque ligne correspond à une annonce immobilière.

________________

# Résultat final

À chaque exécution du workflow (tous les lundis à 08:00), le système produit automatiquement :

- 1 fichier JSON  
- 1 fichier CSV  

Ces fichiers contiennent toutes les annonces immobilières collectées depuis les **15 premières pages de SeLoger**.
