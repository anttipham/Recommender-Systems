import kendall


def calc_satisfaction(group_recs: list[int], user_recs: list[int]) -> float:
    """
    Calculates satisfaction score for one user.

    Satisfaction is defined from the Kendall tau distance between
    the group recommendations and the user's personal recommendations.
    But this value is normalized and adjusted such that the satisfaction score
    of 1 means that the recommendations are identical and 0 means that the
    recommendations are completely different.

    This is similar to the satisfaction score in the course
    material (lecture 7, slide 12) where GroupListSatisfaction is divided by
    a normalizing value (UserListSatisfaction).

    Args:
        group_recs (list[int]): Movie recommendations for the group in the order
                                of best to worst.
        user_recs (list[int]): Personal movie recommendations for one user in
                               the order of best to worst.

    Returns:
        float: Satisfaction score.
    """
    return 1 - kendall.kendall_tau_normalized(group_recs, user_recs)


def next_alpha(satisfactions: list[float]) -> float:
    """
    Calculate next alpha from the satisfaction scores of the previous iteration.

    Alpha is in the range of [0, 1].

    Args:
        satisfactions (list[list[float]]): Satisfaction scores of the previous
                                           iteration for each user.

    Returns:
        float: Next alpha score.
    """
    return max(satisfactions) - min(satisfactions)


def weighted_combination(
    least_misery: list[tuple[int, float]],
    average: list[tuple[int, float]],
    alpha: float,
) -> list[tuple[int, float]]:
    """Ks. luentodia s. 17"""
    pass
