import json

from app.scrapers.castel import CastelScraper

SAMPLE = json.dumps([
    {
        "id": 29860,
        "name": "Café Calvados",
        "permalink": "https://labrulerieducastel.com/produit/cafe-calvados/",
        "is_in_stock": True,
        "prices": {"price": "650", "currency_minor_unit": 2},
    },
    {
        "id": 12345,
        "name": "Café fantôme sans prix",
        "permalink": "https://labrulerieducastel.com/produit/fantome/",
        "is_in_stock": False,
        "prices": {"price": "", "currency_minor_unit": 2},
    },
])


def test_parse_extrait_et_convertit():
    products = CastelScraper().parse(SAMPLE, "https://exemple.test")
    assert products == [{
        "title": "Café Calvados",
        "price_cents": 650,
        "available": True,
        "link": "https://labrulerieducastel.com/produit/cafe-calvados/",
        "external_ref": "29860",
    }]


def test_produit_sans_prix_ignore():
    products = CastelScraper().parse(SAMPLE, "https://exemple.test")
    assert len(products) == 1
