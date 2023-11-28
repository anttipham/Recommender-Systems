class Movie:
    def __init__(
        self, movie_id: int, 
        title: str, 
        genres: str
    ):
        self.movie_id = movie_id
        self.title = title
        self.genres = genres

        self.user_ratings: dict[int, float] = {}
        self.avg_rating: float = None
    
    def __str__(self):
        # NOTE: used for debugging purposes, may want to delete later

        return f"""\
            Movie ID: {self.movie_id}
            Title: {self.title}
            Genres: {self.genres}
            User Ratings: {self.user_ratings}
            Average Rating: {self.avg_rating}
        """