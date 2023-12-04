# Assignment 4: Explanations for Why-not Questions

## Implementation Details and Assumptions

- Missing prediction scores are replaced by a value of 0 in our implementation.
- All assumptions made in the implementation details for previous assigments apply, since their code is reused. This includes the following:
  - The prediction function can give a rating over 5. This is not a mistake, but a property of the prediction formula adding and subtracting the biases (movie mean ratings) of the users.
  - Pearson correlation is used for calculating the similarity between users in the user-based filtering.
  - Movies that some users have already seen can still be recommended to the group if the aggregation methods deems them to be best matches. This is based on the idea that a group member is open to seeing a movie again if everyone else is satisfied with the recommendation, and they liked it.
  - Aggregation methods (average) use either real or predicted ratings for movies when aggregating group recommendations. This is due to many gaps in the dataset (users have often only rated a few movies). Now we can still concider their preferences when performing the group aggregation.
  - All applicable assumptions from previous assingments are assumed, please see their `README.md` files if necessary.

## Running the script
- We suggest creating a conda environment from the `assignment4/requirements.txt` file:
  ```
  conda create --name your_env_name --file requirements.txt
  ```

- User needs to provide path to the MovieLens 100K ratings dataset when calling the script. Call the script inside the `assignment4` directory. Usage:

  ```python
  python assignment4.py <path/to/ml-latest-small/>
  ```

  ml-latest-small is the directory containing the `ratings.csv` and `movies.csv` files.

- We print all results to console output straight from `main`. To change the input parameters (user group members etc.), please see the following global variables in `assignment4.py`

  ```python
  # Number of group recommendations. (This is our k in 'top-k' recommendations.)
  N = 10
  # Analysis limit is used to limit the number of movies analyzed in the explanations
  ANALYSIS_LIMIT = 100
  GROUP = [233, 9, 242]

  # Atomic granularity case
  MOVIE_ATOMIC = "Matrix, The (1999)"
  # Group granularity case
  GENRE = "romance"
  # Position absenteeism case
  MOVIE_ABSENTEEISM = "Fargo (1996)"
  ```

## Design (Score: 40%) and implement (Score: 40%) methods for producing explanations for group recommendations for the granularity case

Our explanation engines (atomic granularity, group granularity, and position absenteeism) are composed from the following categories: error checking, user movie analysis, user genre analysis, group genre analysis, and general analysis.

Error checking is used to check if the input is valid. For example, if the movie does not exist in the database, we can't answer why the movie is not in the recommendations. We also check if the movie is already in the recommendations, or if none of the group members have been given a prediction score for the item etc.

User movie and genre analyses is used to check if the individual users have been given a prediction score for the item high enough to get the item in the recommendations.

Group genre analysis is used to check the group preferences.

General analysis is used to check general reasons why the item is not in the recommendations. For example, the item could be outside the top-10 recommendations due to a tie, or the analysis could recommend the user to ask for a bigger recommendation list etc.

In the beginning of the script, the dataset is loaded appropriately from the `ratings.csv` and `movies.csv` files. It is loaded into a helper `movie` class containing the necessary information explained simplified below:
``` python
class Movie:
  self.movie_id = movie_id
  self.title = title
  self.genres = genres

  # initialize also variables to be updated later on
  # a dict with the user_id, movie_rating for each user for this movie
  self.user_ratings: dict[int, float] = {}

  # the average aggregated group ratings for this movie
  self.avg_rating: float = None
```

Group recommendations are handled as lists of movie_id ints, and the movie objects are stored in a Python `dict[int, Movie]`

### 1. Atomic granularity case: Why not Matrix?

We use this explanation engine for movies that are not in the top-10 group recommendations.

The explanation engine is specialized in movie analyses and contains error checking, user movie analysis, and general movie analysis.

We will next present the answers of the explanation engine in a list format. We include when-conditions if they are needed. Otherwise, we will omit them when the meaning can be understood without them. *For example, the explanation "The movie does not exist in the database." does not need an explicit condition of "When movie does not exist in the database" since it is already clear from the explanation.*

Answers for atomic granularity case:

- Error checking
  - "The movie does not exist in the database."
  - "The movie is already in the recommendations."
  - "None of the group members have been predicted a score for the movie."
- User movie analysis
  - "User has been given a high prediction score for the movie."
  - "User has not been given a prediction score for the movie. This substantially decreases the movie score."
  - "User has not been given a high enough prediction score for the movie. They were given a score lower than the last movie in the recommendations."
- General movie analysis
  - When movie rank is in the range $(10,100]$
    - "The movie rank is outside the group recommendations. You asked for only top 10 movies. You could consider asking top-k to get the movie in the recommendations."
  - When the movie is not in the recommendations due to a tie
    - "The movie has the same score as the last movie in the recommendations, but it was not included in the recommendations because it didn't fit in the top-10 recommendations."
  - "It is possible that the movie is simply not suitable for the group. The movie has received a score of r on average. The other movies could be more suitable for the group."

This explanation engine is implemented in the `assignment4/assignment4.py/atomic_granularity_case` function.

### 2. Group granularity case: Why not romance movies?

We use this explanation engine for various genres in the dataset. This can include analysis regarding genres that are either most or least commmon, or somewhere in between.

The concept of "most common" has been defined as the number of movies in the top-k (or other division) group movie recommendations. This split is done by processing the genres from file `movies.csv` and matching them with the movies and ratings for users from the `ratings.csv` file.

This explanation engine is specialized in genre analyses and contains error checking, user genre analysis, group genre analysis, and general genre analysis.

Answers for group granularity case questions.

- Error checking
  - No movie of this genre is anywhere in the dataset.
    - "The genre does not exist in the database."
  - The mean predicted score for this genre is 0 (Our assumption include that missing values are replaced by 0).
    - "None of the group members have been predicted a score for the genre."

- User genre analysis
  - This includes going over the top-k movies ana a
  - "User has not been given a prediction for a movie of this genre"
  - "User has been given high predicted scores for movies of this genre, but they could have given even higher predicted scores to get more movies of this genre in the top-k group recommendations."
  - "User hasn't been given high enough predicted scores for movies of the given genre. They have been given X predicted scores which are smaller than the last movie in the top-k recommendations received."

- Group genre analysis
  - This includes checking for the most and least common genres in the top-k recommendations. These are then concidered the 'best' and 'worst' genres in the analysis.
  - If the genre is already the most common amongst the top-k recommendations, we report this to the user.
    - "Genre X is already the most common genre in the top-k recommendations."
  - If the genre is the least common, report this.
    - "Your group does not like movies from genre X."
  - "Your group prefers movies from genre X. This could be the reason why movies from genre Y are not in the recommendations."

- General genre analysis
  - This includes more broad explanations.
  - When extending the recommendations to top-k makes the genre the most common
    - "The genre is the most common when the recommendations are extended to top-k. You could consider asking top-k recommendations to get more movies of the genre in the recommendations."
  - When the genre is not the most common in the recommendations due to a tie
    - "The genre could be the most common in the recommendations, but it is not because the order is not defined for movies with the same score."
  - "It is possible that the genre is simply not suitable for the group. There are x movies of this genre in the group recommendation. The other genres could be more suitable for the group."

Analysis of a group granularity question is implemented in the `assignment4/assignment4.py/group_granularity_case` function. The function follows this overall logic:
1. Split movies into their genres. Get these `dict[genre, list[movie_id]] for all top-k, analysis_limit and all recommendations.

2. Perform error handling.
  2.1 If movies of this genre do not exist in the database, return.
  2.2 No one has abeen recommended a movie of this genre, return.

3. Group analysis
  3.1 Find most common genre from dict
  3.2 Find least commmon genre from the dict

4. General genre analysis
  4.1 For k values between current k and `ANALYSIS_LIMIT` loop and find if extending k would make the genre more common.
  4.2 Find the movies tied for near the end of `k`, and see if rearranging by genre would make it more common.

5. User analysis
  5.1 For movies in the genre, find user specific predicted scores. Compare these to the last movie that made the top-k list.


### 3. Position absenteeism: Why not rank Matrix first?

We use this explanation engine for movies that are in the top-10 group recommendations.

This explanation engine is specialized in both movie and genre analyses and contains error checking, user movie analysis, group genre analysis, and general movie analysis. The explanation engine is mostly the same as the atomic granularity case, but we also include group genre analysis to give the user a more in-depth explanation of why the movie is not higher in the recommendations.

We think that a more in-depth explanation is needed for movies that are already in the recommendations because the user might want to know the small details and possible explanation when asking this specific question.

Answers for position absenteeism:

- Error checking
  - "The movie does not exist in the database."
  - "Can't answer why the movie isn't higher in the recommendations because the movie is not in the recommendations. Use the atomic granularity case instead."
  - "The movie is already the highest in the recommendations."
  - "None of the group members have been predicted a score for the movie."
- User movie analysis
  - "User has been given a high prediction score for the movie."
  - "User has not been given a prediction score for the movie. This substantially decreases the movie score."
  - "User has not been given a high enough prediction score for the movie. They gave a score lower than the first movie in the recommendations."
- Group genre analysis
  - When the movie genre is not the most common genres in the recommendations
    - "Your group prefers the following genres: [list of genres], but the movie is of the following genres: [list of genres]."
- General movie analysis
  - When the movie is not higher in the recommendations due to a tie
    - "The movie has the same score as another movie in the recommendations. The movie was not higher in the recommendations because the order is not defined for movies with the same score."
  - "It is possible that the movie is simply not suitable enough to be higher on the recommendations for the group. The movie has received a score of r on average. The other movies could be more suitable for the group."

This explanation engine is implemented in the `assignment4/assignment4.py/position_absenteeism` function.

## Results

Produce a group of 3 users, and for this group, show the top-10 recommendations, i.e.,
the 10 movies with the highest prediction scores, using the MovieLens 100K rating
dataset. Given this recommendation list, take as input one why-not question example
from each of the above cases and report the corresponding explanations (Score: 10%).

The overall results are compiled with the `assignment4/assignment4.py/main` function.

```txt
## Top-10 Average Recommendations for Group [233, 9, 242] ##

  Rank    Movie ID  Title                                                        Average Rating
------  ----------  ---------------------------------------------------------  ----------------
     1        7361  Eternal Sunshine of the Spotless Mind (2004)                           4.59
     2        5952  Lord of the Rings: The Two Towers, The (2002)                          4.42
     3         318  Shawshank Redemption, The (1994)                                       4.35
     4        2329  American History X (1998)                                              4.27
     5         593  Silence of the Lambs, The (1991)                                       4.21
     6         608  Fargo (1996)                                                           4.2
     7          50  Usual Suspects, The (1995)                                             4.17
     8        4993  Lord of the Rings: The Fellowship of the Ring, The (2001)              4.16
     9        3897  Almost Famous (2000)                                                   4.16
    10         356  Forrest Gump (1994)                                                    4.11

## Why-not Questions Regarding the Recommendations ##

Why wasn't movie Matrix, The (1999) in the recommendation?
1. User 233 has not been given a high enough prediction score for the movie Matrix, The (1999). They were given a score of 4.11 which is lower than the last movie in the recommendations.
2. User 9 has not been given a high enough prediction score for the movie Matrix, The (1999). They were given a score of 3.58 which is lower than the last movie in the recommendations.
3. User 242 has not been given a high enough prediction score for the movie Matrix, The (1999). They were given a score of 3.94 which is lower than the last movie in the recommendations.
4. The movie rank for Matrix, The (1999) is 21 in the recommendations. You asked for only top-10 movies. You could consider asking top-30 to get the movie in the recommendations.
5. It is possible that the movie Matrix, The (1999) is simply not suitable for the group. The movie has received a score of 3.88 on average. The other movies could be more suitable for the group.

Why not more romance movies?
1. Your group prefers drama movies. This could be the reason why romance movies are not in the recommendations.
2. It is possible that the genre is simply not suitable for the group. Only 2 of the top-10 recommendations are romance movies. The other genres could be more suitable for the group.
3. User 233 hasn't been given high enough predicted scores for romance movies. They have been given 7 predicted scores which are smaller than the last movie in the top-10 recommendations received.
4. User 9 hasn't been given high enough predicted scores for romance movies. They have been given 10 predicted scores which are smaller than the last movie in the top-10 recommendations received.
5. User 242 hasn't been given high enough predicted scores for romance movies. They have been given 6 predicted scores which are smaller than the last movie in the top-10 recommendations received.

Why not rank Fargo (1996) first?
1. User 9 has not been given a high enough prediction score for the movie Fargo (1996). They gave a score of 3.96 which is lower than the first movie in the recommendations.
2. User 242 has not been given a high enough prediction score for the movie Fargo (1996). They gave a score of 4.06 which is lower than the first movie in the recommendations.
3. User 233 has not been given a high enough prediction score for the movie Fargo (1996). They gave a score of 4.57 which is lower than the first movie in the recommendations.
4. Your group prefers the following genres: thriller, crime, drama, romance, but the movie Fargo (1996) is of the following genres: comedy, crime, drama, thriller.
5. It is possible that the movie Fargo (1996) is simply not suitable enough to be higher on the recommendations for the group. The movie has received a score of 4.20 on average. The other movies could be more suitable for the group.
```

## Prepare also a short presentation (about 5 slides) to show how your method works (Score: 10%)

This presentation can be found in our repository `assignment4/asg4_presentation.pdf`.