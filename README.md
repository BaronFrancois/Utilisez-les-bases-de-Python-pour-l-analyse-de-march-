
# BookScraping Project

## Description
Ce projet `BookScraping` est un script Python pour extraire des informations sur les livres à partir du site web [Books to Scrape](https://books.toscrape.com). Il récupère des détails comme le titre du livre, la catégorie, la note des critiques, et plus encore...

### Prérequis
- Python 3.10.6 ou supérieur
- Encodage UTF-8 dans la console (`chcp 65001` dans CMD Windows)

## Configuration initiale

### Etape 1: Cloner le projet
Clonez le dépôt sur votre machine locale en utilisant :
```bash
git clone [git@github.com:BaronFrancois/Utilisez-les-bases-de-Python-pour-l-analyse-de-march-.git]
(les crochets sont à supprimer)
```

### Etape 2: Accéder au répertoire du projet
Ouvrez votre terminal ou invite de commande et naviguez dans le répertoire du projet :
```bash
cd chemin_vers_BookScraping/MAIN
```

### Etape 3: Création de l'environnement virtuel
Créez un environnement virtuel pour isoler les dépendances du projet :
- **Windows** :
  ```bash
  python -m venv venv
  ```
- **Mac OS & Linux** :
  ```bash
  python3 -m venv venv
  ```

### Etape 4: Activation de l'environnement virtuel
Activez l'environnement virtuel créé :
- **Windows** :
  ```bash
  .\venv\Scripts\activate
  ```
- **Mac OS & Linux** :
  ```bash
  source venv/bin/activate
  ```
*(Vous devriez voir `(venv)` en début de ligne dans le terminal.)*

### Etape 5: Installation des dépendances
Installez les dépendances requises à l'aide de pip :
```bash
pip install -r requirements.txt
```

### Etape 6: Exécution du script
Lancez le script principal du projet :
- **Windows** :
  ```bash
  python main.py
  ```
- **Mac OS & Linux** :
  ```bash
  python3 main.py
  ```

*(Vous pouvez interrompre l'exécution du script à tout moment avec `Ctrl + C`.)*

### Désactivation de l'environnement virtuel
Une fois le script terminé, désactivez l'environnement virtuel avec :
```bash
deactivate
*(il ne manque pas de 's')*
```
