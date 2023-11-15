def kendall_tau(movies1: list[int], movies2: list[int]) -> int:
    """
    Calculate Kendall tau distance for two groups of movies.
    Movies that are not in both groups are ignored.

    Note: the function fails if there are duplicate movies in one list,
    e.g. kendall_tau([1,2,3,4], [4,2,4,3]) (duplicate 4 in second parameter).
    """

    group1 = set(movies1)
    group2 = set(movies2)

    common = group1 & group2
    n = len(common)

    common1 = [movie for movie in movies1 if movie in common]
    common2 = [movie for movie in movies2 if movie in common]
    cumset2 = {common2[i]: set(common2[i + 1 :]) for i in range(n)}

    tau = 0
    for i in range(n - 1):
        for j in range(i + 1, n):
            if common1[j] not in cumset2[common1[i]]:
                tau += 1

    return tau


def kendall_tau_normalized(movies1: list[int], movies2: list[int]) -> float:
    """
    Calculate normalized Kendall tau distance for two groups of movies.
    Movies that are not in both groups are ignored.

    Normalized Kendall tau distance is in the range [0, 1] where 0 means
    that the groups are identical and 1 means that the groups are completely
    different.

    The function returns 1 if there are 1 or less common movies.

    Note: the function fails if there are duplicate movies in one list.
    """
    group1 = set(movies1)
    group2 = set(movies2)

    common = group1 & group2
    n = len(common)
    if n <= 1:
        return 0

    max_kendall_tau_dist = n * (n - 1) / 2
    return kendall_tau(movies1, movies2) / max_kendall_tau_dist


def max_kendall_tau(
    recommendations: list[int], user_recommendations: dict[int, list[int]]
) -> int:
    """
    Evaluate Kendall tau distance of recommendations for all users.
    Returns the maximum possible Kendall tau distance.
    """

    max_tau = 0
    for user_recommendation in user_recommendations.values():
        tau = kendall_tau_normalized(recommendations, user_recommendation)
        print(tau)
        max_tau = max(tau, max_tau)
    return max_tau
