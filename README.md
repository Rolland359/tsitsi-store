
# Tsitsi Store

- **Author**: ANDRIANAVALONA Maminirina rolland

## Description

Projet e-commerce développé avec Django. Ce dépôt contient l'application back-end et les templates nécessaires pour gérer un catalogue de produits, un panier, le processus de commande, la gestion des utilisateurs et les notifications.

## Utilisation

1. Créer un environnement virtuel et l'activer.
2. Installer les dépendances :

```bash
pip install -r requirement.txt
```

3. Appliquer les migrations :

```bash
python manage.py migrate
```

4. Créer un superutilisateur (si besoin) :

```bash
python manage.py createsuperuser
```

5. Lancer le serveur de développement :

```bash
python manage.py runserver
```

6. Accéder à l'application depuis `http://127.0.0.1:8000/`.

## Ressource

- Framework principal : Django
- Base de données : SQLite (fichier `db.sqlite3`)
- Frontend : templates Django + bibliothèques CSS/JS standard (Bootstrap, etc.)
- Fichiers de configuration principaux : [tsitsistore/settings.py](tsitsistore/settings.py)

## Détails sur les algorithmes utilisés et pourquoi les avoir choisis

- Requêtes et filtrage : utilisation de l'ORM Django pour des requêtes claires et maintenables. Choisi pour la productivité et l'intégration native avec Django.
- Pagination : limitation du nombre d'objets par page pour réduire la charge mémoire et améliorer la latence côté client.
- Caching (le cas échéant) : cache par vue ou fragments de template pour réduire les accès répétés à la base de données et accélérer les pages à fort trafic.
- Recherche et recommandations : approche simple basée sur la correspondance de catégories/attributs produits (similarité par catégorie/tags) — choisie pour sa simplicité d'implémentation et ses performances acceptables sans infrastructure ML dédiée.
- Traitement des commandes : logique transactionnelle via l'ORM (transactions DB) pour garantir la cohérence des stocks et des commandes.

Si vous souhaitez que j'ajoute des sections supplémentaires (ex. architecture, tests, CI/CD, ou exemples d'API), dites-le et je l'ajouterai.
