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
ANALYSIS_LIMIT = 100
GROUP = [233, 9, 242]


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
    if movie_index < ANALYSIS_LIMIT:
        # Ceiling to nearest 10
        top_k = math.ceil((movie_index + 1) / 10) * 10
        explanations.append(
            f"The movie rank for {movie.title} is {movie_index+1} in the "
            "recommendations. You asked for only top-10 movies. You could "
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


def genre_statistics(
    movies: dict[int, Movie],
    movie_recs: list[int],
    limit: int,
) -> tuple[dict[str, float], dict[str, int]]:
    """
    Args:
        limit (int): Cut-off limit of the movie_recs list.

    Returns:
        tuple[dict[str, float], dict[str, int]]: Mean scores and samples
                                                    for each genre.
    """

    scores: dict[str, float] = {}
    samples: dict[str, list[int]] = {}

    for movie_id in movie_recs[:limit]:
        for genre in movies[movie_id].genres:
            if genre not in scores:
                scores[genre] = 0.0
            if genre not in samples:
                samples[genre] = []

            scores[genre] += movies[movie_id].avg_rating
            samples[genre].append(movie_id)
    
    mean_scores = {genre: scores[genre] / len(samples[genre]) for genre in scores}
    return mean_scores, samples


def group_granularity_case(
    movies: dict[int, Movie], movie_recs: list[int], genre: str
) -> list[str]:
    """
    Generates explanations for the group (genre) analysis.

    Args:
        movies (dict[int, Movie]): Movie dictionary where key is movie_id and
            value is Movie object.
        movie_recs (list[int]): List of movie_ids in order of recommendation.
        genre (str): Genre to analyze.
    """

    # Top movies by the genre
    topk_means, topk_genre_samples = genre_statistics(movies, movie_recs, N)
    analysis_means, analysis_genre_samples = genre_statistics(movies, movie_recs, ANALYSIS_LIMIT)
    all_means, all_samples = genre_statistics(movies, movie_recs, len(movie_recs))

    ## Error checking
    # - An item does not exist in the database of the system.
    if genre not in all_means.keys():
        return [f"The genre {genre} does not exist in the database."]
    
    # - Item is already in the recommendations.
    max_samples = max(topk_genre_samples.values(), key=len)
    if genre == max_samples:
        return [f"{genre} is already the most common recommendation genre."]
    
    # - None of group members has rated a comedy.
    if all_means[genre] == 0.0:
        return [f"None of the group members have rated a {genre} movie."]

    # Generate explanations
    explanations: list[str] = []

    ## Group analysis
    topk_best_genre = max(topk_genre_samples, key=lambda k: len(topk_genre_samples[k]))
    explanations.append(
        f"Your group prefers {topk_best_genre} movies. This could be the "
        f"reason why {genre} movies are not in the recommendations."
    )

    topk_worst_genre = min(topk_genre_samples, key=lambda k: len(topk_genre_samples[k]))
    if topk_worst_genre == genre:
        explanations.append(f"Your group does not like {genre} movies.")

    ## General genre analysis
    topk_of_genre = len(topk_genre_samples[genre]) if genre in topk_genre_samples else 0
    explanations.append(
        f"It is possible that the genre is simply not suitable for the group. "
        f"Only {topk_of_genre} of the top-{N} recommendations are {genre} movies."
        f"The other genres could be more suitable for the group."
    )

    # size of top-k: does extending make it the most common?
    if genre not in topk_genre_samples:

        # find if extending to more recommendations makes it the most common
        for k in range(N, ANALYSIS_LIMIT+1, 10):
            _, new_topk_genre_samples = genre_statistics(movies, movie_recs, k)
            new_topk_best_genre = max(new_topk_genre_samples, key=lambda k: len(new_topk_genre_samples[k]))
            if genre == new_topk_best_genre:
                explanations.append(
                    f"The genre {genre} is the most common when the "
                    f"recommendations are extended to top-{k}. "
                    f"You asked for too few movies (top-{N}). "
                )
                break

    # genre is in top-k recommendations
    # find if there is a tie (same movie scores)
    else:
        num_of_ties = 0
        for best_movie in topk_genre_samples[topk_best_genre]:
            best_score = movies[best_movie].avg_rating

            for movie in analysis_genre_samples[genre]:
                is_tie = math.isclose(best_score, movies[movie].avg_rating)
                if is_tie:
                    num_of_ties += 1
        
        if len(topk_genre_samples[topk_best_genre]) == len(topk_genre_samples[genre]) - num_of_ties:
            explanations.append(
                f"The genre {genre} could be the most common in the "
                f"recommendations, but it is not because the order "
                f"is not defined for movies with the same score."
            )


    ## User analysis
    # TODO


    return explanations


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
    # Error checking
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
    # User movie analysis
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

    # Group genre analysis
    # - When the genre is not the best genre in the recommendations
    #   - "Your group prefers genre X movies. This could be the reason why the
    #      genre is not the most common in the recommendations."
    genres = Counter()
    for rec_id in movie_recs[:N]:
        genres.update(movies[rec_id].genres)
    most_common_genres = genres.most_common(len(movie.genres))
    top_genres = set(genre for genre, _ in most_common_genres)
    if set(movie.genres) != top_genres:
        explanations.append(
            "Your group prefers the following genres: "
            f"{', '.join(top_genres)}, but the movie {movie.title} is "
            f"of the following genres: {', '.join(movie.genres)}."
        )

    # General movie analysis
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
    print(len(movies), len(movie_recs))

    print(f"\n## Top-{N} Average Recommendations for Group {GROUP} ##\n")
    pretty_print_recs(movies, movie_recs)

    print("\n## Why-not Questions Regarding the Recommendations ##\n")

    # 1st queston: atomic granularity case
    movie_title = "Matrix, The (1999)"
    movie_id = find_movie_id(movies, movie_title)

    print(f"Why wasn't movie {movie_title} in the recommendation?")
    explanations1 = atomic_granularity_case(movies, movie_recs, movie_id)
    for i, explanation in enumerate(explanations1):
        print(f"{i+1}. {explanation}")
    print()

    # 2nd question: group granularity case
    genre = "romance"
    print(f"Why not more {genre} movies?")
    for idx, exp in enumerate(group_granularity_case(movies, movie_recs, genre)):
        print(f"{idx+1}. {exp}")
    print()

    # 3rd question: position absenteeism case
    movie_title = "Fargo (1996)"
    movie_id = find_movie_id(movies, movie_title)

    print(f"Why not rank {movie_title} first?")
    explanations3 = position_absenteeism(movies, movie_recs, movie_id)
    for i, explanation in enumerate(explanations3):
        print(f"{i+1}. {explanation}")
    print()


if __name__ == "__main__":
    main()
