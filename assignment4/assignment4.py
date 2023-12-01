"""
DATA.ML.360 Recommender Systems - Assignment 4
Main file for the assignment.

Antti Pham, Sophie Tötterström
"""

import argparse
import os
import sys
from collections import Counter

import pandas as pd
from movie import Movie
from tabulate import tabulate

import assignment2 as asg2
import assignment3 as asg3

N = 10
GROUP = [233, 9, 242]


## Why-not Logic
def atomic_granularity_case(
    movies: dict[int, Movie], top10_movies: list[int], movie_id: int
) -> list[str]:
    # TODO antti
    pass


def group_granularity_case(
    movies: dict[int, Movie], movie_recs: list[int], genre: str
) -> list[str]:
    # NOTE only movies with avg_rating >= 3 are valid recommendations
    # for the explanations for the why-not questions.
    # other movies are considered to not be recommendations at all
    for index, id in enumerate(movie_recs):
        if movies[id].avg_rating < 3:
            ignore_rest = index
            break
    movie_recs = movie_recs[:ignore_rest]

    # sort movies by the genre
    movies_by_genre = {}
    for movie_id in movie_recs:
        for gen in movies[movie_id].genres:
            if gen in movies_by_genre.keys():
                movies_by_genre[gen].append(movie_id)
            else:
                movies_by_genre[gen] = [movie_id]

    # start compiling answers
    answers = []

    if not genre in movies_by_genre.keys():
        return [f"There are no {genre} movies in the database."]

    # movies of this genre are recommended, but not in top-N
    if len(movies_by_genre[genre]) > N:
        answers.append(f"You asked for only {N} items.")

    # TODO tie-breaking method

    # calculate average score for each genre
    genre_averages = {}
    for gen, movie_id_list in movies_by_genre.items():
        genre_averages[gen] = sum(movies[id].avg_rating for id in movie_id_list) / len(
            movie_id_list
        )

    worst_genre = min(genre_averages, key=genre_averages.get)
    if worst_genre == genre:
        answers.append(f"The group dislikes {genre} movies.")

    best_genre = max(genre_averages, key=genre_averages.get)
    if best_genre != genre:
        answers.append(f"The group prefers {best_genre} movies.")
        answers.append(
            f"{best_genre} movies scored the highest on average "
            f"({genre_averages[best_genre]:.2f}), while {genre} movies "
            f"scored {genre_averages[genre]:.2f}."
        )

    # goes down to individual movies
    top10_movies = movie_recs[:N]

    # top10_not_in_genre = set(top10_movies) - (movies_by_genre[genre])

    genre_not_in_top10 = set(movies_by_genre[genre]) - set(top10_movies)
    # TODO compile these results ??
    for id in genre_not_in_top10:
        atomic_granularity_case(movies, top10_movies, id)

    answers.append(
        f"{len(genre_not_in_top10)} {genre} movies were rated lower by "
        f"similar users compared to the recommended top-{N} movies."
    )

    """ Irrelevant?
    # find genres of top-10 movies
    top10_movies = movie_recs[:N]
    top10_genres = Counter()
    for movie_id in top10_movies:
        top10_genres.update(set(movies[movie_id].genres))

    # compile answers to "why not more {genre} movies?"
    answers.append(f"Only {top10_genres[genre]}/{top10_genres.total()} of the Top-{N} movies are {genre} movies.")
    answers.append(f"The group prefers {top10_genres.most_common(1)[0][0]} movies.")
    """

    return answers


def position_absenteeism(
    movies: dict[int, Movie], top10_movies: list[int], movie_id: int
) -> list[str]:
    # TODO antti
    pass


## Data Processing
def parse_args():
    """
    Handle command-line args.
    """

    parser = argparse.ArgumentParser(
        description=f"""
            Runs CLI to ask why-not questions regarding the recomendations.\n
            User specific recommendations made with user-collaborative filtering,
            and average aggregated to provide top-{N} for the group.
            Group is set as a global variable in the script ({GROUP}).\n
            """,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # always require a positional path argument
    parser.add_argument(
        "path", help="Path to the local ml-latest-small directory.", type=str
    )

    args = parser.parse_args()
    return args


def read_movielens(dir_path: str) -> pd.DataFrame and pd.DataFrame:
    """
    Read the MovieLens data from the given directory path.

    Args:
        dir_path (str): path to ml-latest-small directory

    Returns:
        pd.DataFrame: user-movie ratings dataframe (ratings.csv)
        pd.DataFrame]: movie-genre dataframe (movies.csv)
    """

    # Read ratings data
    ratings_file_path = os.path.join(dir_path, "ratings.csv")
    ratings = pd.read_csv(ratings_file_path)
    user_movie_df = ratings.pivot(index="userId", columns="movieId", values="rating")

    # Read movies genre data
    movies_file_path = os.path.join(dir_path, "movies.csv")
    movies_genre_df = pd.read_csv(movies_file_path, index_col="movieId")

    return user_movie_df, movies_genre_df


def process_movie_genre_data(movies_genre_df: pd.DataFrame) -> dict[int, Movie]:
    """
    Processes movie genre data into more appropriate data structure

    Args:
        movies_genre_df (pd.DataFrame): movie-genre dataframe from movies.csv

    Returns:
        dict[int, Movie]: movie_id, Movie object
    """

    movies: dict[int, Movie] = {}
    for movie_id, row_data in movies_genre_df.iterrows():
        movie_obj = Movie(
            movie_id, row_data["title"], row_data["genres"].lower().split("|")
        )
        movies[movie_id] = movie_obj
    return movies


def update_movies(
    movies: dict[int, Movie],
    recs: dict[int, list[tuple[int, float]]],
    avg_group_recs: list[tuple[int, float]],
):
    """
    Loops over all movie objects, and updates them with the
    user specific ratings and average group rating.

    Args:
        movies (dict[int, Movie]): all pairs of movie_id, Movie object
        recs (dict[int, list[tuple[int, float]]]): user_id, user specific recs
        avg_group_recs (list[tuple[int, float]]): average aggregated group recs
    """

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
        list[int]: movie recommendation movie_ids in order
    """
    args = parse_args()

    user_movie_df, movies_genre_df = read_movielens(dir_path=args.path)
    movies: dict[int, Movie] = process_movie_genre_data(movies_genre_df)

    # user_id, list of tuples (movie_id, rating)
    recs: dict[int, list[tuple[int, float]]] = asg3.get_movie_ratings_for_users(
        user_movie_df
    )

    # list of tuples (movie_id, avg_rating)
    avg_group_recs: list[tuple[int, float]] = asg2.average_aggregate(
        user_movie_df, recs
    )

    # update movie objects with the most current data
    update_movies(movies, recs, avg_group_recs)

    # get movie recs in order (ids used to fetch objects from movies dict)
    movie_recs: list[int] = asg2.nth_elements(avg_group_recs, 1)

    return movies, movie_recs


def pretty_print_recs(movies: dict[int, Movie], movie_recs: list[int]):
    headers = ["Rank", "Movie ID", "Title", "Average Rating"]
    table_data = []
    for idx, movie_id in enumerate(movie_recs[:N]):
        mov_obj = movies[movie_id]
        table_data.append(
            [idx + 1, movie_id, mov_obj.title, f"{mov_obj.avg_rating:.2f}"]
        )
    table = tabulate(table_data, headers=headers)
    print(table)


def main():
    # Fetch all movie objects with related info, as well as top-10 movie_ids
    movies, movie_recs = read_data()

    print(f"\n## Top-{N} Average Recommendations for Group {GROUP} ##\n")
    pretty_print_recs(movies, movie_recs)

    print(f"\n## Why-not Questions Regarding the Recommendations ##\n")
    movie_id = 1
    genre = "comedy"

    # 1st queston: atomic granularity case
    print()

    # 2nd question: group granularity case
    print(f"Why not more {genre} movies?\n")
    for idx, exp in enumerate(group_granularity_case(movies, movie_recs, genre)):
        print(f"{idx+1}. {exp}")

    # 3rd question: position absenteeism case
    print()


if __name__ == "__main__":
    main()
