"""Calcul des volumes horaires selon le barème officiel UVCI.

Formule officielle : Vhtc = Ic × S
  - Ic : coefficient (selon niveau de complexité ET type d'activité)
  - S  : nombre de séquences (grains)

Barème officiel UVCI (Annexe 2 - Tableau des charges horaires) :

| Niveau | Création (Ic) | Mise à jour (Ic = ½ création) |
|--------|---------------|-------------------------------|
|   1    |     0.40      |             0.20              |
|   2    |     0.75      |             0.375             |
|   3    |     1.50      |             0.75              |

Les coefficients réels lus à l'exécution proviennent de la table
`CoefficientConfig`, paramétrable par l'administrateur via
`PUT /config/coefficients`. Les constantes ci-dessous servent de barème
de référence et de fallback si la table est vide.
"""

from typing import Optional
from sqlalchemy.orm import Session


BASE_RATES = {
    1: 0.40,
    2: 0.75,
    3: 1.50,
}

UPDATE_COEFFICIENT = 0.5


OFFICIAL_BAREME = [
    (1, "creation",    0.40),
    (1, "mise_a_jour", 0.20),
    (2, "creation",    0.75),
    (2, "mise_a_jour", 0.375),
    (3, "creation",    1.50),
    (3, "mise_a_jour", 0.75),
]


def _fallback_rate(niveau_complexite: int, type_activite: str) -> float:
    base = BASE_RATES.get(niveau_complexite, 0.0)
    if type_activite == "mise_a_jour":
        return base * UPDATE_COEFFICIENT
    return base


def get_coefficient(
    niveau_complexite: int,
    type_activite: str,
    db: Optional[Session] = None,
) -> float:
    """Récupère le coefficient applicable.

    Priorité : table `CoefficientConfig` (paramétrage admin) -> barème officiel hardcodé.
    """
    if db is not None:
        from app.models.models import CoefficientConfig
        row = (
            db.query(CoefficientConfig)
            .filter(
                CoefficientConfig.niveau_complexite == niveau_complexite,
                CoefficientConfig.type_activite == type_activite,
            )
            .first()
        )
        if row is not None:
            return row.coefficient
    return _fallback_rate(niveau_complexite, type_activite)


def calculate_volume_horaire(
    type_activite: str,
    niveau_complexite: int,
    nb_sequences: int,
    db: Optional[Session] = None,
) -> float:
    """Calcule Vhtc = Ic × S, arrondi à 2 décimales."""
    rate = get_coefficient(niveau_complexite, type_activite, db)
    return round(nb_sequences * rate, 2)
