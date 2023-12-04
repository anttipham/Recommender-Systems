# Assignment 4: Explanations for Why-not Questions

## Implementation Details and Assumptions

- All assumptions made in the implementation details for previous assigments apply, since their code is reused. This includes the following:
  - The prediction function can give a rating over 5. This is not a mistake, but a property of the prediction formula adding and subtracting the biases (movie mean ratings) of the users.
  - Movies that some users have already seen can still be recommended to the group if the aggregation methods deems them to be best matches. This is based on the idea that a group member is open to seeing a movie again if everyone else is satisfied with the recommendation, and they liked it.
  - Aggregation methods (average) use either real or predicted ratings for movies when aggregating group recommendations. This is due to many gaps in the dataset (users have often only rated a few movies). Now we can still concider their preferences when performing the group aggregation.

## Running the script

- User needs to provide path to the MovieLens 100K ratings dataset when calling the script. Call the script inside the `assignment4` directory. Usage:

  ```python
  python assignment3.py <path/to/ml-latest-small/>
  ```

  ml-latest-small is the directory containing the ratings.csv and movies.csv files.

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

Error checking is used to check if the input is valid. For example, if the movie does not exist in the database, we can't answer why the movie is not in the recommendations. We also check if the movie is already in the recommendations, or if none of the group members have rated the item etc.

User movie and genre analyses is used to check if the individual users have rated the item high enough to get the item in the recommendations.

Group genre analysis is used to check the group preference.

General analysis is used to check general reasons why the item is not in the recommendations. For example, the item could be outside the top-10 recommendations due to a tie, or the analysis could recommend the user to ask for a bigger recommendation list etc.

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

### 2. Group granularity case: Why not action movies?

We use this explanation engine for genres that are not the most common in the group recommendations.

This explanation engine is specialized in genre analyses and contains error checking, user genre analysis, group genre analysis, and general genre analysis.

Answers for group granularity case:

- Error checking
  - "The genre does not exist in the database."
  - "The genre is already the most common genre in the recommendations."
  - "None of the group members have been predicted a score for the genre."
- User genre analysis
  <!-- - TODO: Sophie. Muista myös päivittää rating -> prediction score yms.
  - "User has given a high rating for movies of this genre, but they could have given an even higher rating to get more movies of the genre in the recommendations."
  - "User has not rated a movie of this genre."
  - "User X hasn't given a high enough rating for movies of this genre. They gave a rating of which is lower than the last movie in the recommendations." -->
- Group genre analysis
  - "Your group prefers genre X, but the movie genre is Y."
  <!-- TODO: Sophie. Jätetään tämä pois? Tän vois yhdistää yllä olevan rivin kanssa.
  - When the genre is the least common in the recommendations
    - "Your group dislikes the genre." -->
- General genre analysis
  - When extending the recommendations to top-k makes the genre the most common
    - "The genre is the most common when the recommendations are extended to top-k. You could consider asking top-k recommendations to get more movies of the genre in the recommendations."
  - When the genre is not the most common in the recommendations due to a tie
    - "The genre could be the most common in the recommendations, but it is not because the order is not defined for movies with the same score."
  - "It is possible that the genre is simply not suitable for the group. There are x movies of this genre in the group recommendation. The other genres could be more suitable for the group."

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

## Results

Produce a group of 3 users, and for this group, show the top-10 recommendations, i.e.,
the 10 movies with the highest prediction scores, using the MovieLens 100K rating
dataset. Given this recommendation list, take as input one why-not question example
from each of the above cases and report the corresponding explanations (Score: 10%).

## Prepare also a short presentation (about 5 slides) to show how your method works (Score: 10%)
