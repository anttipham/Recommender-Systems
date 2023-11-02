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
USER_ID = 1


# handle command-line args
def parse_args():
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


# read data
def read_movielens(path):
    ratings = pd.read_csv(os.path.join(path, "ratings.csv"))

    # Display 10 first rows of the ratings data
    print(f"Ratings downloaded, number of ratings: {ratings.shape[0]}")
    print(ratings.head(N))

    # create new dataframe where
    # userIds become the rows aka index
    # movieIds become the columns
    # ratings for each movie are placed in the cells accordingly
    user_movie_matrix = ratings.pivot(
        index="userId", columns="movieId", values="rating"
    )
    return user_movie_matrix


# calculate pearson correlation between users
def pearson_corr(user_movie_matrix, user1, user2):
    # find movies both users have rated
    user1_data = user_movie_matrix.loc[user1].dropna().to_frame()
    user2_data = user_movie_matrix.loc[user2].dropna().to_frame()
    common = user1_data.index.intersection(user2_data.index)

    if len(common) < 2:
        return 0  # No common movies

    user1_ratings = user1_data.loc[common].values
    user2_ratings = user2_data.loc[common].values

    user1_mean = user1_data.mean().values[0]
    user2_mean = user2_data.mean().values[0]

    numerator = sum((user1_ratings - user1_mean) * (user2_ratings - user2_mean))
    denominator = np.sqrt(sum((user1_ratings - user1_mean) **2)) \
                * np.sqrt(sum((user2_ratings - user2_mean) **2))

    if denominator == 0:  # handle no variance in one user's ratings
        return 0
    return (numerator / denominator)[0]


# calculate pearson correlation for all users against active user
def get_similar_users(user_movie_matrix, user_id):
    corrs = []
    for other_user in user_movie_matrix.index:
        if other_user != user_id:
            corr = pearson_corr(user_movie_matrix, user_id, other_user)
            corrs.append((other_user, corr))
    corrs.sort(key=lambda x: x[1], reverse=True)
    return corrs


# print top-N most similar users to active user
def print_similar_users(user_movie_matrix, user_id):
    print(f"Top-{N} most similar users to user {user_id}")
    similar_users = get_similar_users(user_movie_matrix, user_id)
    for user, _ in similar_users[:N]:
        print(user)


# Return the top N movies for user a that user a has not seen before.
def print_top_movies(user_movie_df: pd.DataFrame, user_id: int) -> None:
    similar_users = get_similar_users(user_movie_df, user_id)[:N]
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

        if denominator == 0:
            return 0
        return a_mean + numerator / denominator

    # Movies that user a has not rated
    movies = user_movie_df[user_movie_df[user_id].isnull()].columns.astype(int)
    # Predict ratings for movies
    predictions = [(movie, predict(user_movie_df, movie)) for movie in movies]
    predictions.sort(key=lambda x: x[1], reverse=True)

    # Print top N movies
    print(f"Top-{N} most relevant movies for user {USER_ID}")
    for movie, _ in predictions[:N]:
        print(movie)


# TODO sophie calculate different similarity between users, cosine similarity???


def main():
    path = parse_args()

    # a)
    print("## a) download and display rating data")
    user_movie_matrix = read_movielens(path)
    print()

    # b) and c)
    print(
        "## b) c) User-based Collaborative Filtering Approach,"
        "pearson correlation between users"
        "prediction function for movie scores ##"
    )
    print(
        "The functions are implemented in the print_similar_users "
        "and print_top_movies functions"
    )
    print()

    # d)
    print(
        "## d) select user, show 10 most similar users and 10 most relevant movies ##"
    )
    print_similar_users(user_movie_matrix, USER_ID)
    print()
    print_top_movies(user_movie_matrix, USER_ID)
    print()

    # e)
    # e) design and implement new similarity function


if __name__ == "__main__":
    main()
