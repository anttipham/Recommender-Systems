"""
DATA.ML.360 Recommender Systems - Assignment 2
Antti Pham, Sophie Tötterström
"""

import numpy as np
import pandas as pd

import assignment1 as assig1

N = 10
# Two similar users, one dissimilar
GROUP = [233, 609, 238]
SIMILARITY_TYPE = "pearson"


def predict_without_similar_users(
    users_rec: dict[int, list[tuple[int, float]]], user_id: int, movie_id: int
) -> float:
    """
    Predict rating for a movie with precomputated values
    """

    for movie, rating in users_rec[user_id]:
        if movie == movie_id:
            return rating
    raise ValueError("Movie not found")


def get_group_recs(
    users_recs: dict[int, list[tuple[int, float]]]
) -> dict[int, list[tuple[int, float]]]:
    """
    Restructure the user specific recommendations to be more suitably
    formatted for group recommendation aggregation

    Args:
        users_recs (dict[int, list[tuple[int, float]]]): dict with list of
            top-N recommendations tuple[movie_id, rating] for each user

    Returns:
        dict[int, tuple[int, float]]: dict with the movies recommended to all
            users in the group and their predicted ratings for these users,
            where keys are the movie_ids and the values are tuples of users
            and their predicted ratings

    """

    group_recs = {}
    for user, recs in users_recs.items():
        for movie, pred_rating in recs[:N]:
            if movie not in group_recs:
                group_recs[movie] = []
            group_recs[movie].append((user, pred_rating))
    return group_recs


def get_rating(
    user_movie_df: pd.DataFrame,
    users_recs: dict[int, list[tuple[int, float]]],
    user: int,
    movie: int,
) -> float:
    """
    Either get real rating for the movie from user or predict it
    """

    rating = user_movie_df.loc[user, movie]
    if np.isnan(rating):
        rating = predict_without_similar_users(users_recs, user, movie)
    # TODO decide if we want this logic
    # if movie has been seen by user, set rating to 0 to avoid seeing it again
    # else:
    #    rating = 0
    return rating


def get_sorted_group_recs(pred_ratings: dict[int, float]) -> list[tuple[int, float]]:
    """
    Sort group recommendations by predicted rating
    """

    sorted_group_recs = sorted(pred_ratings.items(), key=lambda x: x[1], reverse=True)
    return sorted_group_recs[:N]


def average_aggregate(
    user_movie_df: pd.DataFrame, users_recs: dict[int, list[tuple[int, float]]]
) -> list[tuple[int, float]]:
    """
    Perform average aggregation on recommendations for a group of users
    """

    # first gather recommendations for each member of the group
    group_recs: dict[int, list[tuple[int, float]]] = get_group_recs(users_recs)

    # now perform the average aggregation
    avg_pred_ratings: dict[int, float] = {}
    for movie, user_ratings in group_recs.items():
        # add the recommended movie ratings
        total = sum(nth_elements(user_ratings, 2))

        # find ratings for users who this movie was not recommended to
        not_recommended_to = set(GROUP) - set(nth_elements(user_ratings, 1))
        for user in not_recommended_to:
            total += get_rating(user_movie_df, users_recs, user, movie)

        # now we have the total for this movie, lets perform calculation
        avg_pred_ratings[movie] = total / len(GROUP)

    return get_sorted_group_recs(avg_pred_ratings)


def least_misery_aggregate(
    user_movie_df: pd.DataFrame, users_recs: dict[int, list[tuple[int, float]]]
) -> list[tuple[int, float]]:
    """
    Perform least misery aggregation on recommendations for a group of users
    """

    # first gather recommendations for each member of the group
    group_recs: dict[int, list[tuple[int, float]]] = get_group_recs(users_recs)

    # now perform the average aggregation
    least_misery_pred_ratings = {}
    for movie, user_ratings in group_recs.items():
        # add the recommended movie ratings
        ratings = nth_elements(user_ratings, 2)

        # find ratings for users who this movie was not recommended to
        not_recommended_to = set(GROUP) - set(nth_elements(user_ratings, 1))
        for user in not_recommended_to:
            rating = get_rating(user_movie_df, users_recs, user, movie)
            ratings.append(rating)

        # now we have the total for this movie, lets perform calculation
        least_misery_pred_ratings[movie] = min(ratings)

    return get_sorted_group_recs(least_misery_pred_ratings)


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

    Normalized Kendall tau distance is in the range [0, 1] where 1 means
    that the groups are identical and 0 means that the groups are completely
    different.

    The function returns 0 if there are 1 or less common movies.

    Note: the function fails if there are duplicate movies in one list.
    """
    group1 = set(movies1)
    group2 = set(movies2)

    common = group1 & group2
    n = len(common)
    if n <= 1:
        return 0

    max_kendall_tau = n * (n - 1) / 2
    return 1 - (kendall_tau(movies1, movies2) / max_kendall_tau)


def nth_elements(l: list[tuple[int, float]], n: int) -> list[int]:
    """
    Get nth elements from a list of tuples.
    For example, if n = 1, then the first elements are returned.
    """
    return [el[n - 1] for el in l]


def max_kendall_tau(
    recommendations: list[int], user_recommendations: dict[int, list[int]]
) -> int:
    """
    Evaluate Kendall tau distance of recommendations for all users.
    Returns the maximum possible Kendall tau distance.
    """

    max_tau = 0
    for user_recommendation in user_recommendations.values():
        tau = kendall_tau(recommendations, user_recommendation)
        max_tau = max(tau, max_tau)
    return max_tau


def main():
    ratings_file_path = assig1.parse_args()
    user_movie_df = assig1.read_movielens(ratings_file_path)

    ## a)
    print("Predicting movie ratings for each user")
    recs: dict[int, list[tuple[int, float]]] = {}
    for user in GROUP:
        recs[user] = assig1.get_top_movies(user_movie_df, user, SIMILARITY_TYPE)

    print("Aggregating data")
    avg_group_recs = average_aggregate(user_movie_df, recs)
    least_misery_group_recs = least_misery_aggregate(user_movie_df, recs)
    avg_recs = nth_elements(avg_group_recs, 1)
    least_misery_recs = nth_elements(least_misery_group_recs, 1)

    # Displaying results
    print(f"\n## Top-{N} Recommendations for group {GROUP} ##")
    print("Average aggregation: ")
    for movie in avg_recs:
        print(f"{movie}")

    print("\nLeast misery aggregation: ")
    for movie in least_misery_recs:
        print(f"{movie}")

    ## b)
    kendall_tau_avg = max_kendall_tau(
        avg_recs, {user: nth_elements(recs[user], 1) for user in recs}
    )
    kendall_tau_least_misery = max_kendall_tau(
        least_misery_recs, {user: nth_elements(recs[user], 1) for user in recs}
    )
    print("b)")
    print(
        "The max Kendall tau distance for average aggregation is:",
        kendall_tau_avg,
    )
    print(
        "The max Kendall tau distance for least misery aggregation is:",
        kendall_tau_least_misery,
    )
    print("Thus the best is average aggregation.")


if __name__ == "__main__":
    main()
