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

- An item does not exist in the database of the system.
  - "Action does not exist in the database."
- Number of returned top-k items.
  - "You asked for few items."
- The tie-breaking method
  - "Action had the same score as comedy"

- Movie A is not suitable for the group.
- "Your group prefers \[most common genre\] movies"
- "Your group dislikes action movies"
- None of group members has rated a comedy.
- "Only 1 action movie is in the group top-10 recommendations"
- Only x group members like comedies.

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
