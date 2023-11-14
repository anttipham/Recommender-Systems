# Assignment 2: Group recommendations

## Implementation Details and Assumptions

- movies that some users have already seen can still be recommended to the group if they are highly rated
- aggregationg methods use either real or predicted ratings for movies when aggregating group recommendations
- we allow ratings over 5 due to prediction function not forbidding it and it allows us to maintain order (if everything above 5 would become 5, a lot of predictions would be equal with each other even if factually they aren't)
## Results

### a)

#### Average method

The main idea behind this approach is that all members are considered equals. So, the rating of an item for a group of users will be given be averaging the scores of an item across all group members.

#### Least misery method

One member can act as a veto for the rest of the group. In this case, the rating of an item for a group of users is computed as the minimum score assigned to that item in all group members recommendations.

#### Produce a group of 3 users, and for this group, show the top-10 recommendations that (i) the average method suggests, and (ii) the least misery method suggest

### b)

#### Define a way for counting the disagreements between the users in a group

From the course material, we found Kendall tau distance (among others) to be a good way to measure the disagreements between users in a group. Kendall tau distance is a metric that counts the pairwise disagreements of two rankings. Thus, the higher the Kendall tau distance, the more the rankings disagree.

A way to calculate Kendall tau distance is to count the number of pairs of items that are in different order in the two rankings. The number of pairs of items that are in different order in the two rankings is the Kendall tau distance.

For example, if we have two rankings:

- `Ranking A: 1, 2, 3, 4`
- `Ranking B: 3, 2, 1, 4`

The Kendall tau distance is 3, since there are 3 pairs of items that are in different order: (1, 2), (1, 3), (2, 3).

The Kendall tau distance requires that the two rankings have the same items. Thus, our method will first compute the intersection of the two rankings, and then compute the Kendall tau distance.

#### Propose a method that takes disagreements into account when computing suggestions for the group

We could use a method where we try to minimize the Kendall tau distance of the average or least misery method.

1. We will first compute the Kendall tau distance between a user in the group and the average method. We will repeat this for each user in the group, and sum the values.
2. We will then repeat the same process for the least misery method.
3. Choose the method with the lowest Kendall tau distance.

#### Implement your method and explain why it is useful when producing group recommendations

#### Use again the group of 3 users, and for this group, show the top-10 recommendations, i.e., the 10 movies with the highest prediction scores that your method suggests. Use the MovieLens 100K rating dataset

#### Prepare also a short presentation (about 5 slides) to show how your method works in Assignment 2, Part (b)
