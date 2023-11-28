"""
DATA.ML.360 Recommender Systems - Assignment 4
Main file for the assignment.

Antti Pham, Sophie Tötterström
"""

import assignment1 as asg1
import assignment2 as asg2
import assignment3 as asg3



class Movie:
    def __init__(
        self, movie_id: int, 
        title: str, 
        genres: str
    ):

        self.movie_id = movie_id
        self.title = title
        self.genres = genres

        self.user_ratings = {}
        self.avg_rating = None
 
 
def new_parser():
    pass


# why-not logic
def atomic_granularity_case(
    movies: dict[int, Movie], top10_movies: list[Movie], movie_id: int
) -> list[str]:
    pass


def group_granularity_case(
    movies: dict[int, Movie], top10_movies: list[Movie], movie_id: int
) -> list[str]:
    pass


def position_absenteeism(
    movies: dict[int, Movie], top10_movies: list[Movie], movie_id: int
) -> list[str]:
    pass


def main():
    # Read data
    user_movie_df = asg1.read_movielens(ratings_file_path=asg1.parse_args())


    # key: user_id 
    # value: list of tuples (movie_id, rating)
    recs: dict[int, list[tuple[int, float]]] = asg3.get_movie_ratings_for_users(user_movie_df)

    # list of tuples (movie_id, avg_rating)
    avg_group_recs: list[tuple(int, float)] = asg2.average_aggregate(user_movie_df, recs)


    # ensin luetaan data movies.csv (missä on genret)
    # movie_id, movie_title, genres
    # TODO make movie object
    dict[movie_id, Movie]

    
    top10_movies: list[int] = asg2.nth_elements(avg_group_recs, 1)
    


    print(avg_group_recs)

if __name__ == "__main__":
    main()
