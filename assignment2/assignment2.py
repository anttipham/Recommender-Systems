"""
DATA.ML.360 Recommender Systems - Assignment 2
Antti Pham, Sophie Tötterström
"""


"""
DATA.ML.360 Recommender Systems - Assignment 1
Antti Pham, Sophie Tötterström
"""

import argparse
import os

import pandas as pd
import numpy as np

N = 10
GROUP = [233, 322, 423]

#############################################
######## FUNCTIONS FROM ASSIGNMENT 1 ########

def parse_args():
    """
    Handle command-line args
    """
    parser = argparse.ArgumentParser(
        description="Script for recommender system for MovieLens Dataset"
    )
    parser.add_argument(
        "ratingsfile",
        help="Path to the ratings.csv file",
    )
    args = parser.parse_args()
    return args.ratingsfile

def read_movielens(ratings_file_path):
    """
    Read the MovieLens data from ratings_file_path
    """
    ratings = pd.read_csv(ratings_file_path)

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

def predict(
    user_movie_df: pd.DataFrame, movie_id: int, similar_users, user_id
    ) -> float:

        pearson_for_user = dict(similar_users)
        
        # Mean of the rating for user a
        a = user_id
        a_mean = user_movie_df.loc[a].mean()

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

def get_top_movies(
    user_movie_df: pd.DataFrame, user_id: int, similarity_type="pearson"
) -> list[tuple[int, float]]:
    """
    Returns top N matching movies for a given user
    """

    similar_users = get_similar_users(user_movie_df, user_id, similarity_type)[:N]

    # Movies that user a has not rated
    movies = user_movie_df[user_movie_df[user_id].isnull()].columns.astype(int)
    
    # Predict ratings for movies
    predictions = [
        (movie, predict(user_movie_df, movie, similar_users, user_id)) 
        for movie in movies]
    
    predictions.sort(key=lambda x: x[1], reverse=True)
    return predictions

#############################################
######### FUNCTIONS FOR ASSIGNMENT 2 ########

def predict_without_similar_users(
    user_movie_df, user_id, movie_id, similarity_type):
    """
    Predict rating for a movie without previously having similar users
    """

    similar_users = get_similar_users(
        user_movie_df, user_id, similarity_type)[:N]
    return predict(user_movie_df, movie_id, similar_users, user_id)

def get_group_recs(users_recs):
    """
    Get recommendations for the group of users
    """

    group_recs = {}
    for user, recs in users_recs.items():
        for movie, pred_rating in recs:
            if movie not in group_recs:
                group_recs[movie] = []
            group_recs[movie].append((user, pred_rating))
    return group_recs

def get_rating(user_movie_df, user, movie, similarity_type):
    """
    Either get real rating for the movie from user or predict it
    """

    rating = user_movie_df.loc[user, movie]
    if np.isnan(rating):
        # get predicted rating
        rating = predict_without_similar_users(
            user_movie_df, user, movie, similarity_type)
    return rating

def get_sorted_group_recs(pred_ratings):
    """
    Sort group recommendations by predicted rating
    """

    sorted_group_recs = sorted(
        pred_ratings.items(), key=lambda x: x[1], reverse=True)
    return sorted_group_recs[:N]

def average_aggregate(user_movie_df, users_recs, similarity_type):
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
                total += get_rating(user_movie_df, user, movie, similarity_type)
        
        # now also add the recommended movie ratings
        total = sum(pred_rating for _, pred_rating in user_ratings)

        # now we have the total for this movie, lets perform calculation
        avg_pred_ratings[movie] = total / len(GROUP)

    return get_sorted_group_recs(avg_pred_ratings)

def least_misery_aggregate(user_movie_df, users_recs, similarity_type):
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
                rating = get_rating(user_movie_df, user, movie, similarity_type)
                ratings.append(rating)
        
        # now also add the recommended movie ratings
        ratings.extend([pred_rating for _, pred_rating in user_ratings])

        # now we have the total for this movie, lets perform calculation
        least_misery_pred_ratings[movie] = min(ratings)

    return get_sorted_group_recs(least_misery_pred_ratings)


def main():

    similarity_type = "pearson"
    ratings_file_path = parse_args()
    user_movie_df = read_movielens(ratings_file_path)

    ## a)
    # Fetching data
    recs = {}
    for user in GROUP:
        recs[user] = get_top_movies(user_movie_df, user, similarity_type)[:N]

    # Aggregating data
    avg_group_recs = average_aggregate(user_movie_df, recs, similarity_type)
    least_misery_group_recs = least_misery_aggregate(user_movie_df, recs, similarity_type)

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

