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


def parse_args():
    """
    Handle command-line args
    """

    parser = argparse.ArgumentParser(
        description=f"Script for recommender system for MovieLens Dataset. \n \
            User specific recommendations made with user-collaborative filtering, \
            and Top-{N} average aggregated for the group. \n \
            Runs a CLI to ask why-not questions regarding the recomendations."
    )

    # always require a positional path argument
    parser.add_argument(
        "path",
        help="Path to the local ml-latest-small directory.",
        type=str
    )

    # always require the question type (1 of the 2 options)
    parser.add_argument(
        "-wnt",
        "--why_not_type", 
        choices=["granularity", "position_absenteeism"],
        help="Pick one of the two why-not question types.",
        type=str,
        required=True
    )

    # Determine the requirement of each argument dependent on question type
    gran_q = "granularity" in sys.argv
    atomic_q = "-mg" in sys.argv or "--movie_id_gran" in sys.argv
    group_q = "-g" in sys.argv or "--genre" in sys.argv

    if group_q and atomic_q:
        raise ValueError("Cannot have both -g and -mg arguments.")
    elif gran_q and not atomic_q and not group_q:
        raise ValueError("Must have either -g or -mg argument.")

    granularity_group = parser.add_argument_group("Group Granularity Options")
    granularity_group.add_argument(
        "-mg",
        "--movie_id_gran",
        help="Movie ID for atomic group granularity",
        type=int,
        required=gran_q and atomic_q
    )
    granularity_group.add_argument(
        "-g",
        "--genre",
        help="Genre for group granularity (required for group)",
        type=str,
        required=gran_q and group_q
    )

    pos_abs_group = parser.add_argument_group("Position Absenteeism Options")
    pos_abs_group.add_argument(
        "-ma",
        "--movie_id_abs",
        help="Movie ID for position absenteeism",
        type=int,
        required="position_absenteeism" in sys.argv
    )

    args = parser.parse_args()
    return args


def call_funcs(args, movies, top10_movies):

    explanations = [] # TODO change to set if explanations may be repeated
    if args.why_not_type == "granularity":
        if args.movie_id_gran is not None:
            print("Your why-not question is an atomic granularity question.")
            pass
        elif args.genre is not None:
            print("Your why-not question is a group granularity question.")
            explanations.extend(group_granularity_case(movies, top10_movies, args.genre))

    elif args.why_not_type == "position_absenteeism":
        print("Your why-not question is a position absenteeism question.")

    return explanations

## why-not logic
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


def main():

    # Read data
    args = parse_args()
    user_movie_df, movies_genre_df = read_movielens(dir_path=args.path)
    movies: dict[int, Movie] = process_movie_genre_data(movies_genre_df)

    # user_id, list of tuples (movie_id, rating)
    recs: dict[int, list[tuple[int, float]]] = asg3.get_movie_ratings_for_users(user_movie_df)

    # list of tuples (movie_id, avg_rating)
    avg_group_recs: list[tuple[int, float]] = asg2.average_aggregate(user_movie_df, recs)

    # add remaining data to the movie objects
    update_movies(movies, recs, avg_group_recs)

    # get top-10 movies (ids used to fetch objects from movies dict)
    top10_movies: list[int] = asg2.nth_elements(avg_group_recs[:N-1], 1)
    
    explanations = call_funcs(args, movies, top10_movies)
    [print(exp) for exp in explanations]


if __name__ == "__main__":
    main()
