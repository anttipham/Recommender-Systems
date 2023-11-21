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
    least_misery: dict[int, float],
    average: dict[int, float],
    alpha: float,
) -> list[tuple[int, float]]:
    """
    Calculate the weighted combination of the group aggregated scores of least 
    misery and average methods, weighted appropriately with the alpha value.

    This is done following the sequential hybrid aggregation model presented in
    course material (lecture 7, slide 17).

    Args:
        least_misery (dict[int, float]): the movie, ratings pairs for the group,
                                         aggregated with the least misery method.
        average (dict[int, float]): the movie, ratings pairs for the group,
                                    aggregated with the average method.
        alpha (float): Alpha value of this iteration.

    Returns:
        list[tuple[int, float]]: The group recommendations in descending order.
    """

    scores: dict[int, float] = {}
    for movie_id, avg_rating in average.items():
        least_rating = least_misery[movie_id]
        scores[movie_id] = (1 - alpha) * avg_rating + alpha * least_rating
    return asg2.get_sorted_group_recs(scores)

