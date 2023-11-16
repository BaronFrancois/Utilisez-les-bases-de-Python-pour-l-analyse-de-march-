 <!-- Python version = Python 3.10.6 -->
 <!-- /!\ Please run 'chcp 65001' into the console to encode the utf 8 for special caracters -->
Comment initialiser le projet BookScraping :

Etape 1
    Ouvrez votre terminal ou invite de commande.

Etape 2
    Utilisez la commande cd pour naviguer dans le répertoire où se trouve le projet.

Etape 3
    Créer un environnement virtuel : 
        windows : python -m venv venv
        Mac Os & Linux : python3 -m venv venv

Etape 4
    Activer l'environnement virtuel :
        windows : .\venv\Scripts\activate
        Mac Os & Linux : source venv/bin/activate
    <!-- Vous devriez voir un (venv) en début de ligne sur le terminal -->

Etape 5
    Installer les dépendances :
        pip install -r requirements.txt

Etape 6
    Exécuter votre script Python :
        python main.py
    ou  python3 main.py

Vous pouvez arretez le script à tout moment avec "ctrl + c"
Une fois fini, vous pouvez desactiver l'environnement virtuel (venv) avec la commande :
    deactivate