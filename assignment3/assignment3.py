def calc_satisfaction(group_recs: list[int], user_recs: list[int]) -> float:
    """
    ks. luentodia s.12
    Sama kuin mitä kalvoilla lukee, eli GroupListSatisfaction jaettuna jollain
    normalisoivalla arvolla.

    Meidän tapauksessa:
        Kendall tau -etäisyys jaettuna jollain tavalla, joka normalisoi
        etäisyyden. Siis d/normalisoiva_arvo (emt. ks. wikipedia).

    Args:
        group_recs (list[int]): Movie recommendations for the group in order.
        user_recs (list[int]): Personal movie recommendations for one user.

    Returns:
        float: Satisfaction score.
    """
    pass


def next_alpha(satisfactions: list[float]) -> float:
    """
    ks. luentodia s. 18

    Args:
        satisfactions (list[list[float]]): Satisfaction scores of the previous
        iteration for each user.

    Returns:
        float: Next alpha score
    """
    pass


def weighted_combination(
    least_misery: list[tuple[int, float]],
    average: list[tuple[int, float]],
    alpha: float,
) -> list[tuple[int, float]]:
    """Ks. luentodia s. 17"""
    pass
