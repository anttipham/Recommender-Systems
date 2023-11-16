"""
DATA.ML.360 Recommender Systems - Assignment 2
Main runner script for assignment 2.

Antti Pham, Sophie Tötterström
"""

import disagreement as disag
import numpy as np
import pandas as pd

import assignment1 as assig1

N = 10
# Two similar users, one dissimilar
GROUP = [233, 322, 423]
SIMILARITY_TYPE = "pearson"


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
    elif rating < 3.5:
        # if user gave the movie below a 3.5 they don't want to see it again
        rating = 0
    return rating


def get_sorted_group_recs(pred_ratings: dict[int, float]) -> list[tuple[int, float]]:
    """
    Sort group recommendations by predicted rating
    """

    sorted_recs = sorted(pred_ratings.items(), key=lambda x: x[1], reverse=True)
    return sorted_recs


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

    return nth_elements(get_sorted_group_recs(avg_pred_ratings), 1)


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

    return nth_elements(get_sorted_group_recs(least_misery_pred_ratings), 1)


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
    avg_recs = average_aggregate(user_movie_df, recs)
    least_misery_recs = least_misery_aggregate(user_movie_df, recs)

    # Displaying results
    print(f"\n## Top-{N} Recommendations for group {GROUP} ##")
    print("Average aggregation: ")
    for movie in avg_recs[:N]:
        print(f"{movie}")

    print("\nLeast misery aggregation: ")
    for movie in least_misery_recs[:N]:
        print(f"{movie}")

    ## b)
    # Limit number of recommendations to compare
    recs_list = [nth_elements(reccs, 1) for reccs in recs.values()]
    mod_kemeny_young = disag.modified_kemeny_young(recs_list, N)

    print("\nModified Kemeny-Young aggregation: ")
    for movie in mod_kemeny_young:
        print(f"{movie}")


if __name__ == "__main__":
    main()
