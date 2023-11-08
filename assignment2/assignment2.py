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
USER_ID = 233


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


def main():
    ratings_file_path = parse_args()
    user_movie_df = read_movielens(ratings_file_path)


if __name__ == "__main__":
    main()
