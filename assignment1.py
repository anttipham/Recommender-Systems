"""
DATA.ML.360 Recommender Systems - Assignment 1

Sophie Tötterström
Antti Pham

"""

import argparse

import pandas as pd
import numpy as np


# handle command-line args
def parse_args():
    parser = argparse.ArgumentParser(description="Script for recommender system for MovieLens Dataset")
    parser.add_argument("--path", "-p", required=True, help="Path to the ml-latest-small directory, remember / at the end")
    args = parser.parse_args()
    return args.path

# read data
def read_movielens():

    ratings = pd.read_csv(f'{PATH}ratings.csv')
    print(f"\n## Ratings downloaded, number of ratings: {ratings.shape[0]} ##")
    print(ratings.head())

    # create new dataframe where
    # userIds become the rows aka index
    # movieIds become the columns
    # ratings for each movie are placed in the cells accordingly
    user_movie_matrix = ratings.pivot(index='userId', columns='movieId', values='rating')
    return user_movie_matrix

# calculate pearson correlation between users
def pearson_corr(user1, user2):
    
    # find movies both users have rated
    all_rated = user_movie_matrix[user_movie_matrix.index.isin([user1, user2])]
    common_rated = all_rated.dropna(axis=1, how='any')

    if common_rated.shape[1] < 2:
        return 0  # No common movies

    user1_ratings = common_rated.loc[user1]
    user2_ratings = common_rated.loc[user2]

    user1_mean = user1_ratings.mean()
    user2_mean = user2_ratings.mean()

    numerator = sum((user1_ratings - user1_mean) * (user2_ratings - user2_mean))
    denominator = np.sqrt(sum((user1_ratings - user1_mean) ** 2)) * np.sqrt(sum((user2_ratings - user2_mean) ** 2))

    if denominator == 0: # handle no variance in one user's ratings
        return 0
    return numerator / denominator

# calculate pearson correlation for all users against active user
def get_n_similar_users(user_id, n):

    corrs = []
    for other_user in user_movie_matrix.index:
        if other_user != user_id:
            corr = pearson_corr(user_id, other_user)
            corrs.append((other_user, corr))
    corrs.sort(key=lambda x: x[1], reverse=True)
    return corrs[:n]

# TODO antti predict rating from active user for given movie
def predict(user_id, movie_id, n):

    user_ratings = user_movie_matrix.loc[user_id]
    similar_users = get_n_similar_users(user_id, n)


# TODO sophie calculate different similarity between users, cosine similarity???



def main():

    global PATH
    PATH = parse_args()

    # a) download and display rating data
    global user_movie_matrix
    user_movie_matrix = read_movielens()

    # b) c) user-based collaborative filtering approach, 
    # pearson correlation between users
    # prediction function for movie scores
    print("\n## User-based Collaborative Filtering Approach ##")
    user_id = 1
    movie_id = 1
    n = 10
    predict(user_id, movie_id, n)

    # d) select user, show 10 most similar users and 10 most relevan movies
    print(f"\n## Top-{n} most similar users to user {user_id} ##")
    similar_users = get_n_similar_users(user_id, n=n)
    for user, _ in similar_users:
        print(user)
    
    print(f"\n## Top-{n} most relevant movies for user {user_id} ##")
    # TODO antti print this

    # e) design and implement new similarity function
    

if __name__ == "__main__":
    main()