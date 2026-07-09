# E-commerce Watch

Plateforme de veille concurrentielle e-commerce : surveillance automatisée des prix et du stock, historisation, détection des changements, alertes et tableau de bord.

Le système scrape périodiquement les catalogues surveillés, enregistre un relevé horodaté de chaque produit, détecte les variations (baisse/hausse de prix, rupture, retour en stock), génère des alertes et les notifie — le tout exposé via une API REST et un dashboard de visualisation.

---

## Fonctionnalités

- **Scraping asynchrone** des catalogues concurrents (httpx + BeautifulSoup), avec architecture extensible (un scraper par source).
- **Historisation des prix** : chaque cycle enregistre un snapshot horodaté par produit, sans écraser les précédents, construisant un historique complet.
- **Détection intelligente** des changements : baisse/hausse de prix, passage en rupture, retour en stock.
- **Alertes** générées en base et notifiées, avec anti-doublon (chaque alerte n'est envoyée qu'une fois).
- **Automatisation** via Celery + Celery Beat : le cycle complet s'exécute tout seul à intervalle régulier.
- **API REST** (FastAPI) avec documentation interactive auto-générée.
- **Dashboard** web affichant la liste des produits et les courbes d'évolution de prix (Chart.js).

---

## Architecture

```
Celery Beat ──> Redis (file) ──> Celery Worker ──> Scraper async (httpx + BeautifulSoup)
                                       │
                                 Normalisation (Pydantic)
                                       │
                              PostgreSQL (snapshots historisés)
                                       │
                                 Détection ──> Alertes
                                       │
                                   Notification

PostgreSQL <──── API FastAPI <──── Dashboard (Chart.js)
```

Le projet est organisé en couches aux responsabilités séparées : les **scrapers** ne connaissent que le web, les **models** que la base, les **services** portent la logique métier (normalisation, détection, notification), l'**API** expose les données, et les **workers** orchestrent.

---

## Stack technique

| Domaine | Technologies |
|---|---|
| Langage | Python 3.12+ (async / await) |
| Scraping | httpx, BeautifulSoup |
| Base de données | PostgreSQL, SQLAlchemy 2.0 (async), Alembic |
| File de tâches | Celery, Redis |
| API | FastAPI, Pydantic, Uvicorn |
| Frontend | HTML, CSS, JavaScript, Chart.js |
| Infrastructure | Docker, docker-compose |

---

## Structure du projet

```
ecommerce-watch/
├── app/
│   ├── config.py              # configuration centralisée (pydantic-settings)
│   ├── main.py                # point d'entrée FastAPI
│   ├── db/                    # engine + session async, base déclarative
│   ├── models/                # modèles SQLAlchemy (competitor, product, snapshot, alert)
│   ├── schemas/               # schémas Pydantic (I/O de l'API)
│   ├── api/routes/            # endpoints REST
│   ├── scrapers/              # scraper de base (abstrait) + un scraper par source
│   ├── services/              # normalisation, détection, notification
│   ├── workers/               # configuration et tâches Celery
│   └── static/                # dashboard (HTML/CSS/JS)
├── migrations/                # migrations Alembic
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Installation

### Prérequis

- Python 3.12+
- Docker et Docker Compose

### Mise en place

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/Noan-abidostricot/ecommerce-watch
   cd ecommerce-watch
   ```

2. Créer et remplir le fichier d'environnement à partir de l'exemple :
   ```bash
   cp .env.example .env
   ```
   Renseigner les valeurs (identifiants base de données, Redis, SMTP...).

3. Installer les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```

4. Lancer l'infrastructure (PostgreSQL + Redis) :
   ```bash
   docker compose up -d
   ```

5. Appliquer les migrations de base de données :
   ```bash
   alembic upgrade head
   ```

---

## Utilisation

### Lancer l'API et le dashboard

```bash
uvicorn app.main:app --reload
```

- Dashboard : `http://127.0.0.1:8000/static/index.html`
- Documentation API interactive : `http://127.0.0.1:8000/docs`

### Lancer l'automatisation

Dans deux terminaux séparés :

```bash
# Worker (exécute les tâches)
celery -A app.workers.celery_app worker --loglevel=info --pool=solo

# Beat (déclenche les tâches à intervalle régulier)
celery -A app.workers.celery_app beat --loglevel=info
```

Le cycle de scraping s'exécutera alors automatiquement selon l'intervalle configuré.

---

## Endpoints de l'API

| Méthode | Endpoint | Description |
|---|---|---|
| GET | `/products` | Liste des produits surveillés |
| GET | `/products/{id}/history` | Historique de prix d'un produit |
| GET | `/alerts` | Liste des alertes détectées |

---

## Notes

Le scraper de démonstration cible [books.toscrape.com](https://books.toscrape.com), un site conçu pour l'entraînement au scraping. L'architecture (scraper de base abstrait + un scraper concret par source) permet d'ajouter de nouvelles sources sans modifier le reste du système.
