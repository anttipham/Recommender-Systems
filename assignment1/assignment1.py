"""
DATA.ML.360 Recommender Systems - Assignment 1

Sophie Tötterström
Antti Pham

"""

import argparse
import os

import pandas as pd
import numpy as np

N = 10
USER_ID = 233


def parse_args():
    """
    Handle command-line args
    """
    parser = argparse.ArgumentParser(
        description="Script for recommender system for MovieLens Dataset"
    )
    parser.add_argument(
        "--path",
        "-p",
        required=True,
        help="Path to the ml-latest-small directory",
    )
    args = parser.parse_args()
    return args.path


def read_movielens(path):
    """
    Read the MovieLens data from local directory
    """
    ratings = pd.read_csv(os.path.join(path, "ratings.csv"))

    # Display 10 first rows of the ratings data
    print(f"Ratings downloaded, number of ratings: {ratings.shape[0]}")
    print(ratings.head(N))

    # create new dataframe where
    # userIds become the rows aka index
    # movieIds become the columns
    # ratings for each movie are placed in the cells accordingly
    user_movie_df = ratings.pivot(index="userId", columns="movieId", values="rating")
    return user_movie_df


def pearson_corr(user_movie_df, user1, user2):
    """
    Calculate pearson correlation between users
    """

    # fetch user data from dataframe
    user1_data = user_movie_df.loc[user1].dropna().to_frame()
    user2_data = user_movie_df.loc[user2].dropna().to_frame()

    # calculate user data means
    user1_mean = user1_data.mean().values[0]
    user2_mean = user2_data.mean().values[0]

    # find common movies between the users
    common = user1_data.index.intersection(user2_data.index)

    # NOTE this means we don't calculate similarity measure when less than 3
    if len(common) < 3:
        return 0

    # fetch user specific values for the common movies
    user1_ratings = user1_data.loc[common].values
    user2_ratings = user2_data.loc[common].values

    numerator = sum((user1_ratings - user1_mean) * (user2_ratings - user2_mean))
    denominator = np.sqrt(sum((user1_ratings - user1_mean) ** 2)) \
                * np.sqrt(sum((user2_ratings - user2_mean) ** 2))
    return (numerator / denominator)[0] if denominator else 0


def cosine_sim(user_movie_df, user1, user2, adjusted=False):
    """
    Calculate cosine similarity between users (either normal or adjusted)
    """

    # fetch user data from dataframe
    user1_data = user_movie_df.loc[user1].dropna().to_frame()
    user2_data = user_movie_df.loc[user2].dropna().to_frame()

    # find common movies between the users
    common = user1_data.index.intersection(user2_data.index)

    # NOTE this means we don't calculate similarity measure when less than 3
    if len(common) < 3:
        return 0

    # fetch user specific values for the common movies
    user1_ratings = user1_data.loc[common].values
    user2_ratings = user2_data.loc[common].values

    # adjusted cosine similarity normalizes the ratings
    if adjusted:
        user1_ratings = user1_ratings - user1_data.mean().values[0]
        user2_ratings = user2_ratings - user2_data.mean().values[0]

    numerator = np.dot(user1_ratings.T, user2_ratings)
    denominator = np.linalg.norm(user1_ratings) * np.linalg.norm(user2_ratings)
    return (numerator / denominator)[0][0] if denominator else 0


def get_similarity(user_movie_df, user1, user2, similarity_type):
    """
    Return similarity value between two users depending on chosen metric
    """

    if similarity_type == "cosine":
        sim = cosine_sim(user_movie_df, user1, user2)
    elif similarity_type == "adjusted_cosine":
        sim = cosine_sim(user_movie_df, user1, user2, adjusted=True)
    else:
        sim = pearson_corr(user_movie_df, user1, user2)
    return sim


def get_similar_users(user_movie_df, user_id, similarity_type):
    """
    Calculate similarity for all users against active user
    """

    sims = []
    for other_user in user_movie_df.index:
        if other_user != user_id:
            sim = get_similarity(user_movie_df, user_id, other_user, similarity_type)
            sims.append((other_user, sim))
    sims.sort(key=lambda x: x[1], reverse=True)
    return sims


def print_similar_users(user_movie_df, user_id, similarity_type="pearson"):
    """
    Print top-N most similar users to active user
    """

    print(f"Top-{N} most similar users to user {user_id}")
    similar_users = get_similar_users(user_movie_df, user_id, similarity_type)
    for user, _ in similar_users[:N]:
        print(user)


def get_top_movies(
    user_movie_df: pd.DataFrame, user_id: int, similarity_type="pearson"
) -> list[tuple[int, float]]:
    similar_users = get_similar_users(user_movie_df, user_id, similarity_type)[:N]
    pearson_for_user = dict(similar_users)
    # Mean of the rating for user a
    a = user_id
    a_mean = user_movie_df.loc[a].mean()

    def predict(user_movie_df: pd.DataFrame, movie_id: int) -> float:
        # Get top N users who have rated the movie and are most similar to user a
        top_n_users = []
        for user, _ in similar_users:
            if pd.isna(user_movie_df.loc[user, movie_id]):
                continue
            top_n_users.append(user)

        numerator = 0
        denominator = 0
        for b in top_n_users:
            b_mean = user_movie_df.loc[b].mean()
            numerator += pearson_for_user[b] * (user_movie_df.loc[b, movie_id] - b_mean)
            denominator += pearson_for_user[b]

        return (a_mean + numerator / denominator) if denominator else 0

    # Movies that user a has not rated
    movies = user_movie_df[user_movie_df[user_id].isnull()].columns.astype(int)
    # Predict ratings for movies
    predictions = [(movie, predict(user_movie_df, movie)) for movie in movies]
    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions


# Return the top N movies for user a that user a has not seen before.
def print_top_movies(
    user_movie_df: pd.DataFrame, user_id: int, similarity_type="pearson"
) -> None:
    predictions = get_top_movies(user_movie_df, user_id, similarity_type)
    # Print top N movies
    print(f"Top-{N} most relevant movies for user {USER_ID}")
    for movie, _ in predictions[:N]:
        print(movie)


def main():
    path = parse_args()

    # a)
    print("## a) download and display rating data")
    user_movie_df = read_movielens(path)
    print()

    # b)
    print("##")
    print(
        "b) User-based Collaborative Filtering Approach, "
        "pearson correlation between users"
    )
    # c)
    print("c) prediction function for movie scores")

    # d)
    print("d) select user, show 10 most similar users and 10 most relevant movies")
    print("##")
    print_similar_users(user_movie_df, USER_ID)
    print()
    print_top_movies(user_movie_df, USER_ID)
    print()

    # e) adjusted cosine similarity
    print("e) design and implement adjusted cosine similarity")
    print("##")
    print_similar_users(user_movie_df, USER_ID, similarity_type="adjusted_cosine")
    print()
    print_top_movies(user_movie_df, USER_ID, similarity_type="adjusted_cosine")
    print()


if __name__ == "__main__":
    main()
