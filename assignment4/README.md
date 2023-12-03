# Assignment 4: Explanations for Why-not Questions

## Implementation Details and Assumptions

## Running the script

## Design (Score: 40%) and implement (Score: 40%) methods for producing explanations for group recommendations for the granularity case

Our explanation engines (atomic granularity, group granularity, and position absenteeism) are composed from the following categories: error checking, user movie analysis, user genre analysis, group genre analysis, and general analysis.

Error checking is used to check if the input is valid. For example, if the movie does not exist in the database, we can't answer why the movie is not in the recommendations. We also check if the movie is already in the recommendations, or if none of the group members have rated the item etc.

User movie and genre analyses is used to check if the individual users have rated the item high enough to get the item in the recommendations.

Group genre analyses is used to check the group preference.

General analysis is used to check general reasons why the item is not in the recommendations. For example, the item could be outside the top-10 recommendations due to a tie, or the analysis could recommend the user to ask for a bigger recommendation list etc.

### 1. Atomic granularity case: Why not Matrix?

We use this explanation engine for movies that are not in the top-10 group recommendations.

The explanation engine contains error checking, user movie analysis, and general movie analysis.

Answers for atomic granularity case:

- Error checking
  - "The movie does not exist in the database."
  - "The movie is already in the recommendations."
  - "None of the group members have rated the movie."
- User movie analysis
  - "User has given a high rating for the movie, but they could have given an even higher rating to get the movie in the recommendations."
  - "User has not rated the movie. This substantially decreases the movie score."
  - "User hadn't given a high enough rating for the movie. They gave a rating of which is lower than the last movie in the recommendations."
- General movie analysis
  - When movie rank is in the range $(10,100]$
    - "The movie rank is outside the group recommendations. You asked for only top 10 movies. You could consider asking top-k to get the movie in the recommendations."
  - When the movie is not in the recommendations due to a tie
    - "The movie has the same score as the last movie in the recommendations, but it was not included in the recommendations because it didn't fit in the top-10 recommendations."
  - "It is possible that the movie is simply not suitable for the group. The movie has received a rating of r on average. The other movies could be more suitable for the group."

### 2. Group granularity case: Why not action movies?

We use this explanation engine for genres that are not the most common in the group recommendations.

This explanation engine contains error checking, user genre analysis, group genre analysis, and general genre analysis.

Answers for group granularity case:

- Error checking
  - "The genre does not exist in the database."
  - "The genre is already the most common genre in the recommendations."
  - "None of the group members have rated a movie of the genre."
- User genre analysis
  <!-- - TODO: Sophie
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

This explanation engine is mostly the same as the atomic granularity case, but we also include group genre analysis to give the user a more in-depth explanation of why the movie is not higher in the recommendations.

Answers for position absenteeism:

- Error checking
  - "The movie does not exist in the database."
  - "Can't answer why the movie isn't higher in the recommendations because the movie is not in the recommendations. Use the atomic granularity case instead."
  - "The movie is already the highest in the recommendations."
  - "None of the group members have rated the movie."
- User movie analysis
  - "User has given a high rating for the movie, but they could have given an even higher rating to get the movie in the recommendations."
  - "User has not rated the movie. This substantially decreases the movie score."
  - "User hadn't given a high enough rating for the movie. They gave a rating which is lower than the first movie in the recommendations."
- Group genre analysis
  - When the movie genre is not the most common genres in the recommendations
    - "Your group prefers the following genres: [list of genres], but the movie is of the following genres: [list of genres]."
- General movie analysis
  - When the movie is not higher in the recommendations due to a tie
    - "The movie has the same score as another movie in the recommendations. The movie was not higher in the recommendations because the order is not defined for movies with the same score."
  - "It is possible that the movie is simply not suitable enough to be higher on the recommendations for the group. The movie has received a rating of r on average. The other movies could be more suitable for the group."

## Results

Produce a group of 3 users, and for this group, show the top-10 recommendations, i.e.,
the 10 movies with the highest prediction scores, using the MovieLens 100K rating
dataset. Given this recommendation list, take as input one why-not question example
from each of the above cases and report the corresponding explanations (Score: 10%).

## Prepare also a short presentation (about 5 slides) to show how your method works (Score: 10%)
