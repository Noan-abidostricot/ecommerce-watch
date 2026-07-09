from app.services.normalizer import clean_price


def test_clean_price_cas_simple():
    assert clean_price("£51.77") == 5177


def test_clean_price_cas_qui_tronquait():
    # avec int(float * 100), ce test échouait : 434 au lieu de 435
    assert clean_price("£4.35") == 435


def test_clean_price_euros_et_espaces():
    assert clean_price(" 12.99€ ") == 1299
