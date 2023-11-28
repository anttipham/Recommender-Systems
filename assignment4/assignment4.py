"""
DATA.ML.360 Recommender Systems - Assignment 4
Main file for the assignment.

Antti Pham, Sophie Tötterström
"""

import os
import argparse

import pandas as pd

from movie import Movie
import assignment2 as asg2
import assignment3 as asg3

N = 10
GROUP = [233, 9, 242]
 

def parse_args():
    """
    Handle command-line args
    """
    parser = argparse.ArgumentParser(
        description="Script for recommender system for MovieLens Dataset"
    )
    parser.add_argument(
        "--path",
        help="Path to the ml-latest-small directory",
    )
    args = parser.parse_args()
    return args


def read_movielens(dir_path):
    """
    Read the MovieLens data from ratings_file_path
    """

    ## Read ratings data
    # create new dataframe where
    # userIds become the rows aka index
    # movieIds become the columns
    # ratings for each movie are placed in the cells accordingly
    ratings_file_path = os.path.join(dir_path, "ratings.csv")
    ratings = pd.read_csv(ratings_file_path)
    user_movie_df = ratings.pivot(index="userId", columns="movieId", values="rating")

    ## Read movies data
    movies_file_path = os.path.join(dir_path, "movies.csv")
    movies_genre_df = pd.read_csv(movies_file_path, index_col="movieId")

    return user_movie_df, movies_genre_df


def process_movie_genre_data(movies_genre_df: pd.DataFrame) -> dict[int, Movie]:
    """ Processes movie genre data into more appropriate data structure

    Args:
        movies_genre_df (pd.DataFrame): movie-genre dataframe from movies.csv

    Returns:
        dict[int, Movie]: movie_id, Movie object
    """

    movies: dict[int, Movie] = {}
    for movie_id, row_data in movies_genre_df.iterrows():
        movie_obj = Movie(
            movie_id, 
            row_data["title"],
            row_data["genres"].split('|')
        )
        movies[movie_id] = movie_obj
    return movies


def preprocess(
    movies: dict[int, Movie],
    recs: dict[int, list[tuple[int, float]]],
    avg_group_recs: list[tuple[int, float]]
):

    # process user specific recommendations
    for user_id, user_recs in recs.items():
        for movie_id, rating in user_recs:
            movies[movie_id].user_ratings[user_id] = rating
    
    # process average aggregated recommendations
    n = 0
    for movie_id, avg_rating in avg_group_recs:
        movies[movie_id].avg_rating = avg_rating

## why-not logic
def atomic_granularity_case(
    movies: dict[int, Movie], top10_movies: list[int], movie_id: int
) -> list[str]:
    pass


def group_granularity_case(
    movies: dict[int, Movie], top10_movies: list[int], genre: int
) -> list[str]:
    pass


def position_absenteeism(
    movies: dict[int, Movie], top10_movies: list[int], movie_id: int
) -> list[str]:
    pass


def main():

    # Read data
    args = parse_args()
    user_movie_df, movies_genre_df = read_movielens(dir_path=args.path)
    movies: dict[int, Movie] = process_movie_genre_data(movies_genre_df)

    # user_id, list of tuples (movie_id, rating)
    recs: dict[int, list[tuple[int, float]]] = asg3.get_movie_ratings_for_users(user_movie_df)

    # list of tuples (movie_id, avg_rating)
    avg_group_recs: list[tuple[int, float]] = asg2.average_aggregate(user_movie_df, recs)

    preprocess(movies, recs, avg_group_recs)

    top10_movies: list[int] = asg2.nth_elements(avg_group_recs[:N], 1)
    print(top10_movies)
    


if __name__ == "__main__":
    main()
