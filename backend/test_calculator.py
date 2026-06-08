"""Tests unitaires du moteur de calcul des volumes horaires (barème officiel UVCI).

Vérifie la formule Vhtc = Ic × S sur les 6 combinaisons (niveau × type) du barème,
la règle « mise à jour = ½ création », l'arrondi à 2 décimales et le fallback hors DB.

Pas de dépendance externe : à lancer avec `python test_calculator.py`.
"""

from app.services.calculator import (
    calculate_volume_horaire,
    get_coefficient,
    OFFICIAL_BAREME,
    UPDATE_COEFFICIENT,
)


def test_bareme_officiel():
    # Création : barème officiel UVCI
    assert get_coefficient(1, "creation") == 0.40
    assert get_coefficient(2, "creation") == 0.75
    assert get_coefficient(3, "creation") == 1.50
    # Mise à jour : moitié de la création
    assert get_coefficient(1, "mise_a_jour") == 0.20
    assert get_coefficient(2, "mise_a_jour") == 0.375
    assert get_coefficient(3, "mise_a_jour") == 0.75


def test_formule_vhtc():
    # Vhtc = Ic × S
    assert calculate_volume_horaire("creation", 2, 1) == 0.75   # 0.75 × 1
    assert calculate_volume_horaire("creation", 2, 4) == 3.0    # 0.75 × 4
    assert calculate_volume_horaire("creation", 3, 10) == 15.0  # 1.50 × 10
    assert calculate_volume_horaire("mise_a_jour", 1, 10) == 2.0  # 0.20 × 10


def test_mise_a_jour_demi_creation():
    for niveau in (1, 2, 3):
        creation = get_coefficient(niveau, "creation")
        maj = get_coefficient(niveau, "mise_a_jour")
        assert maj == creation * UPDATE_COEFFICIENT


def test_arrondi_2_decimales():
    v = calculate_volume_horaire("mise_a_jour", 2, 3)  # 0.375 × 3 = 1.125
    assert v == round(v, 2)


def test_niveau_inconnu_renvoie_zero():
    # Niveau hors barème : pas de coefficient -> volume nul (pas d'exception)
    assert get_coefficient(99, "creation") == 0.0
    assert calculate_volume_horaire("creation", 99, 5) == 0.0


def test_bareme_constants_coherents():
    assert len(OFFICIAL_BAREME) == 6
    for niveau, type_act, coeff in OFFICIAL_BAREME:
        assert get_coefficient(niveau, type_act) == coeff


if __name__ == "__main__":
    print("--- Tests unitaires calculator UVCI ---")
    checks = [
        ("Barème officiel (6 coefficients)", test_bareme_officiel),
        ("Formule Vhtc = Ic × S", test_formule_vhtc),
        ("Mise à jour = 1/2 création", test_mise_a_jour_demi_creation),
        ("Arrondi à 2 décimales", test_arrondi_2_decimales),
        ("Niveau inconnu -> 0", test_niveau_inconnu_renvoie_zero),
        ("Constantes OFFICIAL_BAREME cohérentes", test_bareme_constants_coherents),
    ]
    for i, (label, fn) in enumerate(checks, 1):
        fn()
        print(f"{i}. {label} : ok")
    print("--- Tous les tests passent ---")
