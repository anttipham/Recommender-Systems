"""
DATA.ML.360 Recommender Systems - Assignment 4
Main file for the assignment.

Antti Pham, Sophie Tötterström
"""

import os
import sys
import argparse
from collections import Counter

import pandas as pd

from movie import Movie
import assignment2 as asg2
import assignment3 as asg3

N = 10
GROUP = [233, 9, 242]


## Why-not Logic
def atomic_granularity_case(
    movies: dict[int, Movie], top10_movies: list[int], movie_id: int
) -> list[str]:
    pass


def group_granularity_case(
    movies: dict[int, Movie], top10_movies: list[int], genre: str
) -> list[str]:
    
    # antti: example using Counter
    # find genres of top-10 movies
    top10_genres = Counter()
    for movie_id in top10_movies:
        top10_genres.update(set(movies[movie_id].genres))

    # potential answers to "why not more {genre} movies?"
    answers = []
    answers.append(f"Only {top10_genres[genre]}/{top10_genres.total()} of the Top-{N} movies are {genre} movies.")
    answers.append(f"The group prefers {top10_genres.most_common(1)[0][0]} movies.")

    return answers


def position_absenteeism(
    movies: dict[int, Movie], top10_movies: list[int], movie_id: int
) -> list[str]:
    pass


## Data Processing
def parse_args():
    """
    Handle command-line args
    """

    parser = argparse.ArgumentParser(
        description=f"""
            Runs CLI to ask why-not questions regarding the recomendations.\n
            User specific recommendations made with user-collaborative filtering,
            and average aggregated to provide top-{N} for the group.
            Group is set as a global variable in the script ({GROUP}).\n
            Example Question: Why not more comedy movies?
            Usage: python assignment4.py ../ml-latest-small/ -wnt granularity -g comedy
            """,
            formatter_class=argparse.RawTextHelpFormatter
    )

    # always require a positional path argument
    parser.add_argument(
        "path",
        help="Path to the local ml-latest-small directory.",
        type=str
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
            row_data["genres"].lower().split('|')
        )
        movies[movie_id] = movie_obj
    return movies


def update_movies(
    movies: dict[int, Movie],
    recs: dict[int, list[tuple[int, float]]],
    avg_group_recs: list[tuple[int, float]]
):

    # process user specific recommendations
    for user_id, user_recs in recs.items():
        for movie_id, rating in user_recs:
            movies[movie_id].user_ratings[user_id] = rating
    
    # process average aggregated recommendations
    for movie_id, avg_rating in avg_group_recs:
        movies[movie_id].avg_rating = avg_rating


def read_data() -> dict[int, Movie] and list[int]:
    """
    Process all the data gathering related function calls

    Returns:
        dict[int, Movie]: movie_id, Movie object
        list[int]: top-N movie recommendation movie_ids
    """
    args = parse_args()

    user_movie_df, movies_genre_df = read_movielens(dir_path=args.path)
    movies: dict[int, Movie] = process_movie_genre_data(movies_genre_df)

    # user_id, list of tuples (movie_id, rating)
    recs: dict[int, list[tuple[int, float]]] = asg3.get_movie_ratings_for_users(user_movie_df)

    # list of tuples (movie_id, avg_rating)
    avg_group_recs: list[tuple[int, float]] = asg2.average_aggregate(user_movie_df, recs)

    # update movie objects with the most current data
    update_movies(movies, recs, avg_group_recs)

    # get top-10 movies (ids used to fetch objects from movies dict)
    top10_movies: list[int] = asg2.nth_elements(avg_group_recs[:N-1], 1)

    return movies, top10_movies


def main():
    
    # Fetch all movie objects with related info, as well as top-10 movie_ids
    movies, top10_movies = read_data()

    # NOTE älä muuta/siirrä tätä! tämä on tilapäistä! lupaan
    #q_type = "position_absenteeism"
    #movie_id = 1
    #genre = None

    q_type = "granularity"
    movie_id = None
    genre = "action"

    explanations = []
    if q_type == "granularity":
        if movie_id:
            pass
        elif genre:
            explanations.extend(group_granularity_case(movies, top10_movies, genre))
    elif q_type == "position_absenteeism":
        pass

    for exp in explanations:
        print(exp)


if __name__ == "__main__":
    main()
