# Assignment 4: Explanations for Why-not Questions

## Implementation Details and Assumptions

## Running the script

## Design (Score: 40%) and implement (Score: 40%) methods for producing explanations for group recommendations for the granularity case

### 1. Atomic granularity case: Why not Matrix?
<!-- vähän niinkuin vain individual -->

We use this explanation engine for movies that are not in the group recommendations.

Examples answers for Atomic granularity case:

- Error checking
  - "The movie does not exist in the database."
  - "The movie is already in the recommendations."
  - "None of the group members have rated the movie."
- User analysis
  - "User has given a high rating for the movie, but they could have given an even higher rating to get the movie in the recommendations."
  - "User has not rated the movie. This substantially decreases the movie score."
  - "User hadn't given a high enough rating for the movie. They gave a rating of which is lower than the last movie in the recommendations."
- When movie rank is in the range $(10,100]$
  - "The movie rank is outside the group recommendations. You asked for only top 10 movies. You could consider asking top-k to get the movie in the recommendations."
- When the movie is not in the recommendations due to a tie
  - "The movie has the same score as the last movie in the recommendations, but it was not included in the recommendations because it didn't fit in the top-10 recommendations."
- "It is possible that the movie is simply not suitable for the group. The movie has received a rating of r on average. The other movies could be more suitable for the group."

### 2. Group granularity case: Why not action movies?
<!-- vähän niinkuin vain group -->

Examples answers for Group granularity case:

- Error checking
  - "The genre does not exist in the database."
  - "The genre is already the most common genre in the recommendations."
  - "None of the group members have rated a movie of the genre."
- User analysis
  <!-- - TODO: Sophie
  - "User has given a high rating for movies of this genre, but they could have given an even higher rating to get more movies of the genre in the recommendations."
  - "User has not rated a movie of this genre."
  - "User X hasn't given a high enough rating for movies of this genre. They gave a rating of which is lower than the last movie in the recommendations." -->
- Group analysis
  - "Your group prefers genre X movies. This could be the reason why the genre is not the most common in the recommendations."
  - When the genre is the least common in the recommendations
    - "Your group dislikes the genre."
- When extending the recommendations to top-k makes the genre the most common
  - "The genre is the most common when the recommendations are extended to top-k. You could consider asking top-k recommendations to get more movies of the genre in the recommendations."
- When the genre is not the most common in the recommendations due to a tie
  - "The genre could be the most common in the recommendations, but it is not because the order is not defined for movies with the same score."
- "It is possible that the genre is simply not suitable for the group. There are x movies of this genre in the group recommendation. The other genres could be more suitable for the group."

### 3. Position absenteeism: Why not rank Matrix first?
<!-- käytännössä molemmat -->

We use this explanation engine for movies that are in the group recommendations.

Examples answers for Position absenteeism

- Error checking
  - "The movie does not exist in the database."
  - "Can't answer why the movie isn't higher in the recommendations because the movie is not in the recommendations. Use the atomic granularity case instead."
  - "The movie is already the highest in the recommendations."
  - "None of the group members have rated the movie."
- User analysis
  - "User has given a high rating for the movie, but they could have given an even higher rating to get the movie in the recommendations."
  - "User has not rated the movie. This substantially decreases the movie score."
  - "User hadn't given a high enough rating for the movie. They gave a rating which is lower than the first movie in the recommendations."
- When the movie is not higher in the recommendations due to a tie
  - "The movie has the same score as another movie in the recommendations. The movie was not higher in the recommendations because the order is not defined for movies with the same score."
- "It is possible that the movie is simply not suitable enough to be higher on the recommendations for the group. The movie has received a rating of r on average. The other movies could be more suitable for the group."

<!-- TODO group granularity
- "Your group prefers \[most common genre\] movies"
- "Your group dislikes action movies"
- None of group members has rated a comedy.
- "Only 1 action movie is in the group top-10 recommendations"
- Only x group members like comedies. -->

## Results

Produce a group of 3 users, and for this group, show the top-10 recommendations, i.e.,
the 10 movies with the highest prediction scores, using the MovieLens 100K rating
dataset. Given this recommendation list, take as input one why-not question example
from each of the above cases and report the corresponding explanations (Score: 10%).

## Prepare also a short presentation (about 5 slides) to show how your method works (Score: 10%)
