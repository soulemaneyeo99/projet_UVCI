# Hour calculation grid from the Cahier des Charges:
#
#   Niveau 1 : 0.40 h / sequence
#   Niveau 2 : 0.75 h / sequence
#   Niveau 3 : 1.50 h / sequence
#
#   Update (mise_a_jour) coefficient : 0.5

BASE_RATES = {
    1: 0.40,
    2: 0.75,
    3: 1.50,
}

UPDATE_COEFFICIENT = 0.5


def calculate_hours(nb_sequences: int, niveau_complexite: int, is_update: bool = False) -> float:
    """Legacy helper kept for backward compatibility with the original activities endpoint."""
    rate = BASE_RATES.get(niveau_complexite, 0.0)
    total = nb_sequences * rate
    if is_update:
        total *= UPDATE_COEFFICIENT
    return round(total, 2)


def calculate_volume_horaire(type_activite: str, niveau_complexite: int, nb_sequences: int) -> float:
    """Primary calculation entry-point used by the new activities endpoint."""
    is_update = type_activite == "mise_a_jour"
    return calculate_hours(nb_sequences, niveau_complexite, is_update)
