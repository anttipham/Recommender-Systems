# Assignment 3: Sequential Recommendations

## Implementation Details and Assumptions

Only the top 10 recommendations are used to calculate the $\alpha _j$ value
because normalized Kendall tau distances don't behave well for calculating
a large number of distances for the whole data. Normalization for a
large data returns a value that is often very close to 0, which makes
it difficult to calculate the next recommendation.

## Running the script

- User needs to provide path to the MovieLens 100K ratings dataset when calling the script. Usage:

  ```python
  python assignment3.py <path/to/ml-latest-small/ratings.csv>
  ```

### Design (Score: 30%) and implement (Score: 30%) new method for producing sequential group recommendations

<!-- TODO: Jokin johdanto? -->

#### **Satisfaction**

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

Note that $\tau(R_u, R_G)$ calculates distance of the *common items* in the
recommendation lists.

Satisfaction value calculation is implemented in the `assignment3/assignment3.py/calc_satisfaction` function.

#### **Group Aggregation**

Common group recommendation aggregation methods include the average aggregation, and least misery. These are assumed to be known from assingment 2, however, they are described below.

In average aggregation all members are considered equals. So, the rating of an item for a group of users will be given be averaging the scores of an item across all group members. The movie $i$ group score is equal to the average of predicted ratings for all the group $g$ members, i.e.:

$$
score_g(i) = \frac{ \sum_{u \in g}{\hat{r_{ui}}} }{|g|}
$$

where $r_{ui}$ is the predicted rating for user $u$ item $i$. The problem with this logic is that the outlier (someone with a really high or low score) will never be satisfied. This is  implemented in the `assignment3/assignment2.py/average_aggregate` function.

In least misery aggregation can act as a veto for the rest of the group. In this case, the rating of an item for a group of users is computed as the minimum score assigned to that item in all group members recommendations. The movie $i$ group score is the smallest score any member of the group $g$ has given as a rating $r_{ui}$, i.e.:
$$ score_g(i) = \min_{u \in g}{\hat{r_{ui}}} $$
As one might predict, the recommended movies are unlikely to ilicit strong reactions, either positive or negative. This is  implemented in the `assignment3/assignment2.py/least_misery_aggregate` function.

#### **Sequential Hybrid Aggregation Model**
<!-- Vähän tekstiä että mikä on sequential recommendation -->

To solve the issues with average and least misery aggregation, we combine them in a way which captures the advantages of both methods. This is known as sequential hybrid aggregation.

In this method, the score from both the abovementioned methods are joined with a weighted combination. Thus the group $g$ rating $score$ for the movie $i$ on recommendation iteration $j$ is as follows:

$$ score_g(i, j) = (1 - \alpha _j)*avg\_score_g(i, j) + \alpha _j * least\_score_g(i, j)
$$

The weight of each aggregation method for iteration $j$ depends on the value of $\alpha _j \in [0,1]$. From this definition we see that when $\alpha _j$ is 0, the least misery score is completely ignored, and only the average aggregation score effects the hybrid recommendation score. In this case, the best options for the entire group as a whole are concidered, without giving any additional weight to the users. When $\alpha _j$ is 1, only the least misery score effects the result.
<!-- Lisää sepitystä näistä -->

Weighted combination calculation is implemented in the `assignment3/assignment3.py/weighted_combination` function.

$\alpha _j$ is calculated using the satisfation scores defined above from the previous iteration $j-1$, following the equation

$$
\alpha _j = \max _{u \in g} sat(G_u, G_{score_{j-1}}) - \min _{u \in g} sat(u, G_{score_{j-1}}),
$$

where $G_{score_{j-1}}$ is defined as the top 10 group aggregation scores of
the previous iteration.

<!-- Tekstiä tästä logiikasta-->

Alpha value calculation is implemented in the `assignment3/assignment3.py/next_alpha` function.

#### **Implementation**

The overall algorithm implementation for our proposed sequential hybrid aggregation model is implemented in the `assignment3/assignment3.py/main` function.

### Provide detailed explanations and clarifications about why the method you propose works well for the case of sequential group recommendations (Score: 25%)

<!-- TODO -->

## Results

### Produce a group of 3 users, and for this group, show the top-10 recommendations in 3 different sequences, i.e., the 10 movies with the highest prediction scores in 3 rounds, using the MovieLens 100K rating dataset (Score: 5%)

```txt
## Iteration 1, alpha=0.0 ##
Top-10 Hybrid Recommendations for group [233, 9, 242]
Movie number: 2329,     Predicted rating: 4.13
Movie number: 50,       Predicted rating: 4.09
Movie number: 318,      Predicted rating: 4.08
Movie number: 608,      Predicted rating: 3.96
Movie number: 7361,     Predicted rating: 3.94
Movie number: 4993,     Predicted rating: 3.93
Movie number: 5952,     Predicted rating: 3.93
Movie number: 593,      Predicted rating: 3.91
Movie number: 4011,     Predicted rating: 3.8
Movie number: 296,      Predicted rating: 3.78

## Iteration 2, alpha=0.31 ##
Top-10 Hybrid Recommendations for group [233, 9, 242]
Movie number: 2329,     Predicted rating: 4.17
Movie number: 318,      Predicted rating: 4.16
Movie number: 7361,     Predicted rating: 4.15
Movie number: 50,       Predicted rating: 4.12
Movie number: 5952,     Predicted rating: 4.08
Movie number: 608,      Predicted rating: 4.03
Movie number: 4993,     Predicted rating: 4.0
Movie number: 593,      Predicted rating: 4.0
Movie number: 356,      Predicted rating: 3.88
Movie number: 858,      Predicted rating: 3.87

## Iteration 3, alpha=0.11 ##
Top-10 Hybrid Recommendations for group [233, 9, 242]
Movie number: 2329,     Predicted rating: 4.15
Movie number: 318,      Predicted rating: 4.11
Movie number: 50,       Predicted rating: 4.1
Movie number: 7361,     Predicted rating: 4.02
Movie number: 608,      Predicted rating: 3.99
Movie number: 5952,     Predicted rating: 3.98
Movie number: 4993,     Predicted rating: 3.96
Movie number: 593,      Predicted rating: 3.94
Movie number: 4011,     Predicted rating: 3.82
Movie number: 858,      Predicted rating: 3.81
```

### Prepare also a short presentation (about 5 slides) to show how your method works (Score: 10%)

This presentation can be found in our repository `assignment3/asg3_presentation.pdf`.
