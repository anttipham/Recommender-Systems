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


def main():
    ratings_file_path = assig1.parse_args()
    user_movie_df = assig1.read_movielens(ratings_file_path)

    ## a)
    print("Predicting movie ratings for each user")
    recs = {}
    for user in GROUP:
        recs[user] = assig1.get_top_movies(user_movie_df, user, SIMILARITY_TYPE)

    print("Aggregating data")
    avg_group_recs = average_aggregate(user_movie_df, recs)
    least_misery_group_recs = least_misery_aggregate(user_movie_df, recs)

    # Displaying results
    print(f"\n## Top-{N} Recommendations for group {GROUP} ##")
    print("Average aggregation: ")
    for movie, _ in avg_group_recs:
        print(f"{movie}")

    print("\nLeast misery aggregation: ")
    for movie, _ in least_misery_group_recs:
        print(f"{movie}")

    ## b)
    # TODO results reviewed with disagreements
    # käytännössä fairness * relevance (missä relevance on (a) output)

    # TODO kendall tau


if __name__ == "__main__":
    main()
