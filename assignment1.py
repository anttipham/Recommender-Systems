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
    all_rated = user_movie_matrix[user_movie_matrix.index.isin([user1, user2])]
    common_rated = all_rated.dropna(axis=1, how="any")

    if common_rated.shape[1] < 2:
        return 0  # No common movies

    user1_ratings = common_rated.loc[user1]
    user2_ratings = common_rated.loc[user2]

    user1_mean = user1_ratings.mean()
    user2_mean = user2_ratings.mean()

    numerator = sum((user1_ratings - user1_mean) * (user2_ratings - user2_mean))
    denominator = np.sqrt(sum((user1_ratings - user1_mean) ** 2)) * np.sqrt(
        sum((user2_ratings - user2_mean) ** 2)
    )

    if denominator == 0:  # handle no variance in one user's ratings
        return 0
    return numerator / denominator


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


# predict rating from active user for given movie
def predict(user_movie_df: pd.DataFrame, user_id: int, movie_id: int) -> float:
    a = user_id
    similar_users = get_similar_users(user_movie_df, user_id)
    pearson_for_user = dict(similar_users)

    # Mean of the rating for user a
    a_mean = user_movie_df.loc[a].mean()

    # Top N users who have rated movie and are most similar to user a
    users = user_movie_df[user_movie_df[movie_id].notnull()].index
    top_n_users = [user for user, _ in similar_users if user in users][:N]

    numerator = 0
    denominator = 0
    for b in top_n_users:
        b_mean = user_movie_df.loc[b].mean()
        numerator += pearson_for_user[b] * (user_movie_df.loc[b, movie_id] - b_mean)
        denominator += pearson_for_user[b]

    return a_mean + numerator / denominator


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
    movie_id = 1
    predict(user_movie_matrix, USER_ID, movie_id)
    print()

    # d)
    print("## d) select user, show 10 most similar users and 10 most relevan movies ##")
    print_similar_users(user_movie_matrix, USER_ID)
    print()

    print(f"\n## Top-{N} most relevant movies for user {USER_ID} ##")
    # TODO antti print this

    # e)
    # e) design and implement new similarity function


if __name__ == "__main__":
    main()
