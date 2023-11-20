# Assignment 3: Sequential Recommendations

## Implementation Details and Assumptions

## Running the script

- User needs to provide path to the MovieLens 100K ratings dataset when calling the script. Usage:

  ```python
  python assignment3.py <path/to/ml-latest-small/ratings.csv>
  ```

## Results

### Design a new method for producing sequential group recommendations (Score: 30%)

<!-- Jokin johdanto -->

#### Satisfaction

(We assume that Kendall tau distance is already known from our assignment 2.)

Satisfaction is defined from the Kendall tau distance between
the group recommendations $R_G$ and the user's personal recommendations $R_u$.
But this value is normalized and adjusted such that the satisfaction score
of 1 means that the recommendations are identical and 0 means that the
recommendations are completely different.

Normalization is done by dividing the Kendall tau distance by the maximum
possible distance, which is $\binom{n}{2} = \frac{1}{2}n(n - 1)$, where $n$ is the number
of items in the recommendation list.

Adjustment is done by subtracting the normalized Kendall tau distance from 1.

Thus, the satisfaction score is defined as:

$$
sat(R_u, R_G) = 1 - \frac{\tau(R_u, R_G)}{\frac{1}{2}n(n - 1)}
$$

(This is similar to the satisfaction score in the course
material (lecture 7, slide 12) where GroupListSatisfaction is divided by
a normalizing value, UserListSatisfaction.)

### Implement a new method for producing sequential group recommendations (Score: 30%)

### Provide detailed explanations and clarifications about why the method you propose works well for the case of sequential group recommendations (Score: 25%)

### Produce a group of 3 users, and for this group, show the top-10 recommendations in 3 different sequences, i.e., the 10 movies with the highest prediction scores in 3 rounds, using the MovieLens 100K rating dataset (Score: 5%)

### Prepare also a short presentation (about 5 slides) to show how your method works (Score: 10%)
