"""
DATA.ML.360 Recommender Systems - Assignment 2
File includes logic related to (b) section of the assignment.

Antti Pham, Sophie Tötterström
"""

from itertools import permutations


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


def kendall_tau_disagreement(
    recommendations: list[int], user_recommendations: list[list[int]]
) -> int:
    """
    Evaluate Kendall tau disagreement.
    This is defined as the difference of maximum and minimum distance.
    """
    #tau = 0
    #for user_recommendation in user_recommendations:
    #    tau += kendall_tau(recommendations, user_recommendation)
    #return tau

    min_tau = float("inf")
    max_tau = float("-inf")
    for user_recommendation in user_recommendations:
        tau = kendall_tau(recommendations, user_recommendation)
        if tau < min_tau:
            min_tau = tau
        if tau > max_tau:
            max_tau = tau
    return abs(max_tau - min_tau)


def get_movies(recommendations_list: list[list[int]], n: int) -> list[int]:
    """
    Find n movies that are in all users' recommendations
    """

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


def modified_kemeny_young(recommendations_list: list[list[int]], n: int) -> list[int]:
    """
    Runs a modified version of the Kemeny-Young method.

    Goes through all possible permutations of the recommendations and calculates 
    the disagreement (based on the Kendall tau distance) for each permutation. 
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

    # Get the movies that are in all users' recommendations
    movies = get_movies(recommendations_list, n)

    # Simplify the user recommendations to only contain the common movies
    recommendations_list = [
        [movie for movie in recommendations if movie in movies]
        for recommendations in recommendations_list
    ]
    # print(recommendations_list)
    # print(movies)

    # Find the best permutation (aka order of recommendations)
    best_recs_order: list[int] = []
    min_tau = float("inf")
    for recc_order in permutations(movies):
        tau = kendall_tau_disagreement(recc_order, recommendations_list)
        if tau < min_tau:
            min_tau = tau
            best_recs_order = recc_order

    return best_recs_order
