"""
DATA.ML.360 Recommender Systems - Assignment 4
Main file for the assignment.

Antti Pham, Sophie Tötterström
"""

import argparse
import os
from collections import Counter
import math

import pandas as pd
from movie import Movie
from tabulate import tabulate

import assignment2 as asg2
import assignment3 as asg3

# Number of recommendations
N = 10
# Analysis limit
LIMIT = 100
GROUP = [233, 9, 242]
MOVIE = "Matrix, The (1999)"
GENRE = "action"


def atomic_granularity_case(
    movies: dict[int, Movie], movie_recs: list[int], movie_id: int
) -> list[str]:
    """
    Generates explanations for the atomic granularity case.

    Args:
        movies (dict[int, Movie]): Movie dictionary where key is movie_id and
            value is Movie object.
        movie_recs (list[int]): List of movie_ids in order of recommendation.
        movie_id (int): Movie id of the movie to generate explanations for.

    Returns:
        list[str]: List of explanations.
    """
    # Error checking.
    # - An item does not exist in the database of the system.
    if movie_id not in movie_recs:
        return ["The movie does not exist in the database."]
    movie = movies[movie_id]
    # - Item is already in the recommendations.
    if movie_id in movie_recs[:N]:
        return ["The movie is already in the recommendations."]
    # - None of the group has rated this item
    if movie.avg_rating == 0:
        return [f"None of the group members have rated the movie {movie.title}."]

    # Generate explanations.
    explanations: list[str] = []
    # - x peers like A, but y dislike it
    #   - Like
    #     - User 1: 5.0
    #   - Dislike
    #     - User 1: 3.5
    #     - User 2: 2.0
    last_movie = movies[movie_recs[N - 1]]
    for user_id, user_score in sorted(movie.user_ratings.items(), key=lambda x: x[1]):
        if user_score == 5.0:
            continue
        if user_score >= last_movie.avg_rating:
            explanations.append(
                f"User {user_id} has given a high rating of {user_score:.2f} "
                f"for the movie {movie.title}, but they could have given an "
                "even higher rating to get the movie in the recommendations."
            )
            continue
        if user_score == 0:
            # - User x has no recommendations for this item
            explanations.append(
                f"User {user_id} has not rated the movie {movie.title}. "
                f"This substantially decreases the score for {movie.title}."
            )
            continue
        explanations.append(
            f"User {user_id} hadn't given a high enough rating for "
            f"the movie {movie.title}. "
            f"They gave a rating of {user_score:.2f} which is lower than "
            f"the last movie in the recommendations."
        )
    # - Number of returned top-k items.
    movie_index = movie_recs.index(movie_id)
    if movie_index < LIMIT:
        # Ceiling to nearest 10
        top_k = math.ceil((movie_index + 1) / 10) * 10
        explanations.append(
            f"The movie rank for {movie.title} is {movie_index+1} in the "
            "recommendations. You asked for only top 10 movies. You could "
            f"consider asking top-{top_k} to get the movie in the "
            "recommendations."
        )
    # - The tie-breaking method
    # Float equality check has to be done with isclose() because of
    # floating point arithmetic.
    is_tie = math.isclose(movie.avg_rating, last_movie.avg_rating)
    if is_tie:
        explanations.append(
            f"The movie {movie.title} has the same score as the last movie "
            f"{last_movie.title} in the recommendations, but it was not "
            "included in the recommendations because it didn't fit in the "
            f"top-{N} recommendations."
        )
    # - Movie A is not suitable for the group.
    if not is_tie:
        explanations.append(
            f"It is possible that the movie {movie.title} is simply not "
            "suitable for the group. The movie has received "
            f"a rating of {movie.avg_rating:.2f} on average. "
            "The other movies could be more suitable for the group."
        )
    return explanations


def genre_analysis(
    movies: dict[int, Movie], movie_recs: list[int], genre: list[str]
) -> list[str]:
    """
    Generates explanations for the genre analysis.

    The genre list contains the genres that the analysis generates explanations
    for. The genres are interpreted as a logical AND. For example, if the
    genre list is ["action", "comedy"], then the explanations are generated
    for movies that are both action and comedy movies.

    Args:
        movies (dict[int, Movie]): Movie dictionary where key is movie_id and
            value is Movie object.
        movie_recs (list[int]): List of movie_ids in order of recommendation.
        genre (list[str]): List of genres to analyze.
    """
    # Sort top-M movies by the genre
    movies_by_genre = {}
    for movie_id in movie_recs[:LIMIT]:
        for gen in movies[movie_id].genres:
            if gen in movies_by_genre:
                movies_by_genre[gen].append(movie_id)
            else:
                movies_by_genre[gen] = [movie_id]


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
    movies: dict[int, Movie], movie_recs: list[int], movie_id: int
) -> list[str]:
    """
    Generates explanations for the position absenteeism case.

    Args:
        movies (dict[int, Movie]): Movie dictionary where key is movie_id and
            value is Movie object.
        movie_recs (list[int]): List of movie_ids in order of recommendation.
        movie_id (int): Movie id of the movie to generate explanations for.

    Returns:
        list[str]: List of explanations.
    """
    # Error checking.
    # - An item does not exist in the database of the system.
    if movie_id not in movie_recs:
        return ["The movie does not exist in the database."]
    movie = movies[movie_id]
    # - Item is not in the recommendations.
    if movie_id not in movie_recs[:N]:
        return [
            f"Can't answer why the movie {movie.title} isn't higher "
            "in the recommendations because the movie is not in the "
            "recommendations. Use the atomic granularity case instead."
        ]
    # Item is already the highest in the recommendations.
    if movie_id == movie_recs[0]:
        return [
            f"The movie {movie.title} is already the highest in the recommendations."
        ]
    # - None of the group has rated this item
    if movie.avg_rating == 0:
        return [f"None of the group members have rated the movie {movie.title}."]

    # Generate explanations.
    explanations: list[str] = []
    # - x peers like A, but y dislike it
    #   - Like
    #     - User 1: 5.0
    #   - Dislike
    #     - User 1: 3.5
    #     - User 2: 2.0
    first_movie = movies[movie_recs[0]]
    for user_id, user_score in sorted(movie.user_ratings.items(), key=lambda x: x[1]):
        if user_score == 5.0:
            continue
        if user_score >= first_movie.avg_rating:
            explanations.append(
                f"User {user_id} has given a high rating of {user_score:.2f} "
                f"for the movie {movie.title}, but they could have given an "
                "even higher rating to get the movie in the recommendations."
            )
            continue
        if user_score == 0:
            # - User x has no recommendations for this item
            explanations.append(
                f"User {user_id} has not rated the movie {movie.title}. "
                f"This substantially decreases the score for {movie.title}."
            )
            continue
        explanations.append(
            f"User {user_id} hadn't given a high enough rating for "
            f"the movie {movie.title}. "
            f"They gave a rating of {user_score:.2f} which is lower than "
            f"the first movie in the recommendations."
        )
    # - The tie-breaking method
    # Float equality check has to be done with isclose() because of
    # floating point arithmetic.
    movie_index = movie_recs.index(movie_id)
    for movie_recs_id in movie_recs[:movie_index]:
        rec_movie = movies[movie_recs_id]
        is_tie = math.isclose(movie.avg_rating, rec_movie.avg_rating)
        if is_tie:
            explanations.append(
                f"The movie {movie.title} has the same score as the movie "
                f"{rec_movie.title} in the recommendations. "
                "The movie was not higher in the recommendations because "
                "the order is not defined for movies with the same score."
            )
    # - Movie A is not suitable for the group.
    if not is_tie:
        explanations.append(
            f"It is possible that the movie {movie.title} is simply not "
            "suitable enough to be higher on the recommendations for the "
            "group. The movie has received "
            f"a rating of {movie.avg_rating:.2f} on average. "
            "The other movies could be more suitable for the group."
        )
    # -----------------------------------------------------------------------
    # TODO: group granularity case
    # - "Your group prefers \[most common genre\] movies"
    # - "Your group dislikes action movies"
    # - "Only 1 action movie is in the group top-10 recommendations"
    # - Only x group members like comedies.
    return explanations


## Data Processing
def parse_args() -> argparse.Namespace:
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


def read_movielens(dir_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
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
) -> None:
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


def read_data() -> tuple[dict[int, Movie], list[int]]:
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


def pretty_print_recs(movies: dict[int, Movie], movie_recs: list[int]) -> None:
    headers = ["Rank", "Movie ID", "Title", "Average Rating"]
    table_data = []
    for idx, movie_id in enumerate(movie_recs[:N]):
        mov_obj = movies[movie_id]
        table_data.append(
            [idx + 1, movie_id, mov_obj.title, f"{mov_obj.avg_rating:.2f}"]
        )
    table = tabulate(table_data, headers=headers)
    print(table)


def find_movie_id(movies: dict[int, Movie], movie_title: str) -> int:
    """
    Finds the movie_id for a given movie title.

    Args:
        movies (dict[int, Movie]): movie_id, Movie object
        movie_title (str): movie title

    Returns:
        int: movie_id
    """
    for movie_id, movie_obj in movies.items():
        if movie_obj.title == movie_title:
            return movie_id
    return None


def main():
    # Fetch all movie objects with related info, as well as top-10 movie_ids
    movies, movie_recs = read_data()

    print(f"\n## Top-{N} Average Recommendations for Group {GROUP} ##\n")
    pretty_print_recs(movies, movie_recs)

    print("\n## Why-not Questions Regarding the Recommendations ##\n")
    movie_id = find_movie_id(movies, MOVIE)

    # 1st queston: atomic granularity case
    print(f"Why wasn't movie {MOVIE} in the recommendation?")
    explanations1 = atomic_granularity_case(movies, movie_recs, movie_id)
    for i, explanation in enumerate(explanations1):
        print(f"{i+1}. {explanation}")
    print()

    # 2nd question: group granularity case
    print(f"Why not more {GENRE} movies?")
    for idx, exp in enumerate(group_granularity_case(movies, movie_recs, GENRE)):
        print(f"{idx+1}. {exp}")
    print()

    # 3rd question: position absenteeism case
    print(f"Why not rank {MOVIE} first?")
    explanations3 = position_absenteeism(movies, movie_recs, movie_id)
    for i, explanation in enumerate(explanations3):
        print(f"{i+1}. {explanation}")
    print()


if __name__ == "__main__":
    main()
