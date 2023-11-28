# Assignment 4: Explanations for Why-not Questions

## Implementation Details and Assumptions

## Running the script

## Design (Score: 40%) and implement (Score: 40%) methods for producing explanations for group recommendations for the granularity case

1. Atomic granularity case: Why not Matrix?
2. Group granularity case: Why not action movies?
3. Position absenteeism: Why not rank Matrix first?

Examples answers for Atomic granularity case:

- An item does not exist in the database of the system.
  - "Matrix does not exist in the database."
- Number of returned top-k items.
  - "You asked for few items."
- The tie-breaking method
  - "Matrix had the same score as Iron Man"

- x peers like A, but y dislike it
  - Like
    - User 1: 5.0
  - Dislike
    - User 1: 3.5
    - User 2: 2.0
- None of the group has rated this item
- User x has no recommendations for this item

- Movie A is not suitable for the group.

Examples answers for Group granularity case:

- An item does not exist in the database of the system.
  - "Action does not exist in the database."
<!-- - Number of returned top-k items.
  - "You asked for few items." -->
- The tie-breaking method
  - "Action had the same score as comedy"

- Movie A is not suitable for the group.
- "Your group prefers \[most common genre\] movies"
- "Your group dislikes action movies"
- None of group members has rated a comedy.
- "Only 1 action movie is in the group top-10 recommendations"
- Only x group members like comedies.

Examples answers for Position absenteeism

- An item does not exist in the database of the system.
  - "Matrix does not exist in the database."
- Number of returned top-k items.
  - "You asked for few items."
- The tie-breaking method
  - "Matrix had the same score as Iron Man"

- x peers like A, but y dislike it
  - Like
    - User 1: 5.0
  - Dislike
    - User 1: 3.5
    - User 2: 2.0
- None of the group has rated this item
- User x has no recommendations for this item

- Movie A is not suitable for the group.
- "Your group prefers \[most common genre\] movies"
- "Your group dislikes action movies"
- None of group members has rated a comedy.
- "Only 1 action movie is in the group top-10 recommendations"
- Only x group members like comedies.

## Results

Produce a group of 3 users, and for this group, show the top-10 recommendations, i.e.,
the 10 movies with the highest prediction scores, using the MovieLens 100K rating
dataset. Given this recommendation list, take as input one why-not question example
from each of the above cases and report the corresponding explanations (Score: 10%).

## Prepare also a short presentation (about 5 slides) to show how your method works (Score: 10%)
