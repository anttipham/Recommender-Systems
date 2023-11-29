class Movie:
    """
    Class describing a movie object of MovieLens dataset
    """

    def __init__(
        self, movie_id: int, 
        title: str, 
        genres: list[str]
    ):
        """
        Args:
            movie_id (int): movie id
            title (str): movie title (with year)
            genres (str): list of genres
        """

        self.movie_id = movie_id
        self.title = title
        self.genres = genres

        # initialize also variables to be updated later on
        # a dict with the user_id, movie_rating for each user for this movie
        self.user_ratings: dict[int, float] = {}

        # the average aggregated group ratings for this movie
        self.avg_rating: float = None
    
    def __str__(self):
        """
        String method for printing information about the movie object.
        Used for debugging purposes.
        """

        return f"""\
            Movie ID: {self.movie_id}
            Title: {self.title}
            Genres: {self.genres}
            User Ratings: {self.user_ratings}
            Average Rating: {self.avg_rating}
        """