"""
DATA.ML.360 Recommender Systems - Assignment 2
Antti Pham, Sophie Tötterström
"""

import numpy as np

import assignment1 as assig1

N = 10
GROUP = [233, 322, 423]
SIMILARITY_TYPE = "pearson"


def predict_without_similar_users(
    users_rec: dict[int, dict[int, float]], user_id, movie_id
):
    """
    Predict rating for a movie with precomputated values
    """
    for movie, rating in users_rec[user_id]:
        if movie == movie_id:
            return rating
    raise ValueError("Movie not found")


def get_group_recs(users_recs):
    """
    Get recommendations for the group of users
    """

    group_recs = {}
    for user, recs in users_recs.items():
        for movie, pred_rating in recs[:N]:
            if movie not in group_recs:
                group_recs[movie] = []
            group_recs[movie].append((user, pred_rating))
    return group_recs


def get_rating(user_movie_df, users_recs, user, movie):
    """
    Either get real rating for the movie from user or predict it
    """

    rating = user_movie_df.loc[user, movie]
    if np.isnan(rating):
        # get predicted rating
        rating = predict_without_similar_users(users_recs, user, movie)
    return rating


def get_sorted_group_recs(pred_ratings):
    """
    Sort group recommendations by predicted rating
    """

    sorted_group_recs = sorted(pred_ratings.items(), key=lambda x: x[1], reverse=True)
    return sorted_group_recs[:N]


def average_aggregate(user_movie_df, users_recs):
    """
    Perform average aggregation on recommendations for a group of users
    """

    # first gather recommendations for each member of the group
    group_recs = get_group_recs(users_recs)

    # now perform the average aggregation
    avg_pred_ratings = {}
    for movie, user_ratings in group_recs.items():
        # find ratings for users who this movie was not recommended to
        total = 0
        for user in GROUP:
            if not any(user_id == user for user_id, _ in user_ratings):
                total += get_rating(user_movie_df, users_recs, user, movie)

        # now also add the recommended movie ratings
        total = sum(pred_rating for _, pred_rating in user_ratings)

        # now we have the total for this movie, lets perform calculation
        avg_pred_ratings[movie] = total / len(GROUP)

    return get_sorted_group_recs(avg_pred_ratings)


def least_misery_aggregate(user_movie_df, users_recs):
    """
    Perform least misery aggregation on recommendations for a group of users
    """

    # first gather recommendations for each member of the group
    group_recs = get_group_recs(users_recs)

    # now perform the average aggregation
    least_misery_pred_ratings = {}
    for movie, user_ratings in group_recs.items():
        ratings = []

        # find ratings for users who this movie was not recommended to
        for user in GROUP:
            if not any(user_id == user for user_id, _ in user_ratings):
                rating = get_rating(user_movie_df, users_recs, user, movie)
                ratings.append(rating)

        # now also add the recommended movie ratings
        ratings.extend([pred_rating for _, pred_rating in user_ratings])

        # now we have the total for this movie, lets perform calculation
        least_misery_pred_ratings[movie] = min(ratings)

    return get_sorted_group_recs(least_misery_pred_ratings)


def kendall_tau(movies1: list[int], movies2: list[int]) -> int:
    """
    Calculate Kendall tau distance for two groups of movies.
    Movies that are not in both groups are ignored.
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


def first_elements(l: list[tuple[int, float]]) -> list[int]:
    """
    Get first elements from a list of tuples.
    """
    return [movie for movie, _ in l]


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
    avg_recs = first_elements(avg_group_recs)
    least_misery_recs = first_elements(least_misery_group_recs)

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
        avg_recs, {user: first_elements(recs[user]) for user in recs}
    )
    kendall_tau_least_misery = max_kendall_tau(
        least_misery_recs, {user: first_elements(recs[user]) for user in recs}
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
