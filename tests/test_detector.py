from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.services.detector import detect_changes


class FakeSession:
    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)


def snapshot(price: int, in_stock: bool = True) -> PriceSnapshot:
    return PriceSnapshot(product_id=1, price=price, in_stock=in_stock)


def produit() -> Product:
    return Product(id=1, name="x", url="http://x", competitor_id=1)


def test_baisse_de_prix():
    session = FakeSession()
    detect_changes(session, produit(), snapshot(2000), snapshot(1500))
    assert [a.alert_type for a in session.added] == ["price_drop"]


def test_prix_stable_aucune_alerte():
    session = FakeSession()
    detect_changes(session, produit(), snapshot(2000), snapshot(2000))
    assert session.added == []


def test_rupture_de_stock():
    session = FakeSession()
    detect_changes(session, produit(), snapshot(2000, True), snapshot(2000, False))
    assert [a.alert_type for a in session.added] == ["out_of_stock"]


def test_baisse_et_retour_en_stock_deux_alertes():
    session = FakeSession()
    detect_changes(session, produit(), snapshot(2000, False), snapshot(1500, True))
    assert {a.alert_type for a in session.added} == {"price_drop", "back_in_stock"}
