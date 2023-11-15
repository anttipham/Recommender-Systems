import itertools


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


# def kendall_tau_normalized(movies1: list[int], movies2: list[int]) -> float:
#     """
#     Calculate normalized Kendall tau distance for two groups of movies.
#     Movies that are not in both groups are ignored.

#     Normalized Kendall tau distance is in the range [0, 1] where 0 means
#     that the groups are identical and 1 means that the groups are completely
#     different.

#     The function returns 1 if there are 1 or less common movies.

#     Note: the function fails if there are duplicate movies in one list.
#     """
#     group1 = set(movies1)
#     group2 = set(movies2)

#     common = group1 & group2
#     n = len(common)
#     if n <= 1:
#         return 0

#     max_kendall_tau_dist = n * (n - 1) / 2
#     return kendall_tau(movies1, movies2) / max_kendall_tau_dist


# def kendall_tau_disagreement(
#     recommendations: list[int], user_recommendations: dict[int, list[int]]
# ) -> int:
#     """
#     Evaluate Kendall tau disagreement.
#     This is defined as the difference of maximum and minimum distance.
#     """
#     max_tau = 0
#     min_tau = 1
#     for user_recommendation in user_recommendations.values():
#         tau = kendall_tau_normalized(recommendations, user_recommendation)
#         print(tau)
#         max_tau = max(tau, max_tau)
#         min_tau = min(tau, min_tau)
#     return max_tau - min_tau


def kemeny_young(recommendations_list: list[list[int]], n: int) -> list[int]:
    """
    Runs the Kemeny-Young method.

    Goes through all possible permutations of the recommendations and
    calculates the Kendall tau distance for each permutation.
    The permutation with the lowest distance is returned.

    The function goes through all permutations, so the time complexity is O(n!*n^2).

    Movies are chosen in the order of
    - the first movies of all the users
    - the second movies of all the users
    - the third movies of all the users
    - etc.

    Args:
        recommendations_list (list[list[int]]): List of list of user's recommendations.

    Returns:
        list[int]: A n-sized list of movies in the order of the best permutation.

    Raises:
        ValueError: If there are not enough common movies in the recommendations.
    """

    def get_movies() -> list[int]:
        common_movies = set(recommendations_list[0])
        for i in range(1, len(recommendations_list)):
            common_movies &= set(recommendations_list[i])

        # Find n movies that are in all users' recommendations
        # Go in the order of
        # 1st movie of 1st user, 1st movie of 2nd user, ...,
        # 2nd movie of 1st user, 2nd movie of 2nd user, ...,
        # 3rd movie of 1st user, 3rd movie of 2nd user, ..., etc
        movies_list = []
        for nth_movies in zip(*recommendations_list):
            for movie in nth_movies:
                if movie in common_movies and movie not in movies_list:
                    movies_list.append(movie)
                if len(movies_list) > n:
                    movies_list = movies_list[:n]
                    return movies_list
        raise ValueError("Not enough common movies")

    # Get the movies that are in all users' recommendations
    movies = get_movies()
    # Simplify the user recommendations to only contain the common movies
    recommendations_list = [
        [movie for movie in recommendations if movie in movies]
        for recommendations in recommendations_list
    ]
    # print(recommendations_list)
    # print(movies)
    # Find the best permutation
    best_permutation: list[int] = []
    min_tau = float("inf")
    for permutation in itertools.permutations(movies):
        tau = kendall_tau(permutation, movies)
        if tau < min_tau:
            min_tau = tau
            best_permutation = permutation

    return best_permutation
