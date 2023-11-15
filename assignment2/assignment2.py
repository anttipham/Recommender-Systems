"""
DATA.ML.360 Recommender Systems - Assignment 2
Antti Pham, Sophie Tötterström
"""

import numpy as np
import pandas as pd

import assignment1 as assig1

N = 10
KENDALL_COMPARE_N = 50
# Two similar users, one dissimilar
# GROUP = [233, 609, 238]
GROUP = [233, 322, 423]
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
        for movie, pred_rating in recs:
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
    return sorted_group_recs


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


def nth_elements(l: list[tuple[int, float]], n: int) -> list[int]:
    """
    Get nth elements from a list of tuples.
    For example, if n = 1, then the first elements are returned.
    """
    return [el[n - 1] for el in l]


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
    for movie in avg_recs[:N]:
        print(f"{movie}")

    print("\nLeast misery aggregation: ")
    for movie in least_misery_recs[:N]:
        print(f"{movie}")

    ## b)
    # user_recommendations = {
    #     user: nth_elements(recs[user], 1)[:KENDALL_COMPARE_N] for user in recs
    # }
    # average_recommendations = avg_recs[:KENDALL_COMPARE_N]
    # least_misery_recommendations = least_misery_recs[:KENDALL_COMPARE_N]

    # kendall_tau_avg = max_kendall_tau(average_recommendations, user_recommendations)
    # print("b)")
    # print(
    #     "The max normalized Kendall tau distance for average aggregation is:",
    #     kendall_tau_avg,
    # )
    # kendall_tau_least_misery = max_kendall_tau(
    #     least_misery_recommendations, user_recommendations
    # )
    # print(
    #     "The max normalized Kendall tau distance for least misery aggregation is:",
    #     kendall_tau_least_misery,
    # )
    # print("Thus the best is average aggregation.")


if __name__ == "__main__":
    main()
