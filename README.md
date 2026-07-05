# Dimensionnement NG-RAN 5G

Application de bureau (Tkinter) permettant de calculer le **dimensionnement d'un réseau 5G (NG-RAN)** à partir des paramètres radio, de couverture et de capacité.

## Fonctionnalités

- Calcul du bilan de liaison (MAPL) et des marges (shadowing, pénétration, interférences)
- Estimation de la portée maximale d'une cellule (modèle 3GPP UMa LOS)
- Calcul du nombre de sites nécessaires pour la **couverture**
- Calcul du nombre de sites nécessaires pour la **capacité** (trafic, MIMO, efficacité spectrale)
- Recommandation finale du nombre de sites à déployer
- Export du rapport de résultats au format `.txt`

## Prérequis

- Python 3.8 ou supérieur
- Tkinter (généralement inclus avec Python ; sous Linux : `sudo apt install python3-tk`)

## Installation

```bash
git clone https://github.com/<ton-nom-utilisateur>/dimensionnement-5g.git
cd dimensionnement-5g
```

Aucune dépendance externe n'est requise (uniquement la bibliothèque standard Python).

## Utilisation

```bash
python dimensionnement_5g.py
```

1. Renseigner les paramètres généraux, de couverture et de capacité/trafic
2. Cliquer sur **"Lancer le calcul"**
3. Consulter les résultats affichés
4. Cliquer sur **"Exporter le rapport"** pour sauvegarder un fichier `.txt` récapitulatif

## Auteur

Projet personnel / académique de dimensionnement réseau 5G.

## Licence

Ce projet est distribué sous licence MIT (voir le fichier `LICENSE`).
