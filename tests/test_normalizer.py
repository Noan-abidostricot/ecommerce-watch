from app.services.normalizer import normalize


def test_normalize_construit_product_data():
    raw = {
        "title": "Café Calvados",
        "price_cents": 650,
        "available": True,
        "link": "https://exemple.test/produit",
        "external_ref": "29860",
    }
    data = normalize(raw)
    assert data.price_cents == 650
    assert data.external_ref == "29860"


def test_normalize_sans_external_ref():
    raw = {
        "title": "Livre",
        "price_cents": 1399,
        "available": True,
        "link": "https://exemple.test/livre",
    }
    assert normalize(raw).external_ref is None
