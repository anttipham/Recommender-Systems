# Assignment 2: Group recommendations

## Implementation Details and Assumptions

- The prediction function can give a rating over 5. This is not a mistake, but a property of the prediction formula adding and subtracting the biases (movie mean ratings) of the users.
- Movies that some users have already seen can still be recommended to the group if the aggregation methods deems them to be best matches. This is based on the idea that a group member is open to seeing a movie again if everyone else is satisfied with the recommendation, and they liked it.
- Aggregation methods in (a) use either real or predicted ratings for movies when aggregating group recommendations. This is due to many gaps in the dataset (users have often only rated a few movies). Now we can still concider their preferences when performing the group aggregation.

## Running the script

- We print all results to console output straight from `main`. To change anything around (user group members etc.), please see the following global variables in `assignment2.py`

    ```python
    N = 10
    GROUP = [233, 322, 423]
    SIMILARITY_TYPE = "pearson"
    ```

- User needs to provide path to the MovieLens 100K ratings dataset when calling the script. Usage:

    ```python
    python assignment2.py <path/to/ml-latest-small/ratings.csv>
    ```

- Script takes a minute or so to finish running everything, so please be patient.

## Results

### a)

#### **Produce a group of 3 users, and for this group, show the top-10 recommendations that (i) the average method suggests, and (ii) the least misery method suggests.**

We have chosen a group of 3 users, where two are similar to each other and 1 is not. This allows for more variety in the results. Users selected are `GROUP = [233, 322, 423]`. The top-10 results for this group are shown below for the MovieLens 100K rating dataset.

#### **Average method**

The main idea behind this approach is that all members are considered equals. So, the rating of an item for a group of users will be given be averaging the scores of an item across all group members. The movie $i$ group score is equal to the average of predicted ratings for all the group $g$ members, i.e.:
$$ score_g(i) = \frac{ \sum_{u \in g}{\hat{r_{ui}}} }{|g|} $$
where $r_{ui}$ is the predicted rating for user $u$ item $i$. Then the items are ordered based on these scores, and the top-N rankings provided as a result.

This aggregation approach is implemented in the `assignment2.py/average_aggregate` function. Below are the top-10 results for our `GROUP` using this method.

```txt
Average aggregation:
7361
296
608
34
318
610
4979
2329
3897
112
```


#### **Least misery method**

One member can act as a veto for the rest of the group. In this case, the rating of an item for a group of users is computed as the minimum score assigned to that item in all group members recommendations. The movie $i$ group score is the smallest score any member of the group $g$ has given as a rating $r_{ui}$, i.e.:
$$ score_g(i) = \min_{u \in g}{\hat{r_{ui}}} $$
Again, the items are ordered based on these scores, and the top-N rankings provided as a result.

This aggregation approach is implemented in the `assignment2.py/least_misery_aggregate` function. Below are the top-10 results for our `GROUP` using this method.

```txt
Least misery aggregation:
7361
608
2329
4979
34
2959
318
2571
296
112
```

### b)

#### **Define a way for counting the disagreements between the users in a group**

From the course material, we found Kendall tau distance, and we wanted to use this metric to calculate disagreements between users in a group.

##### Kendall tau distance

Kendall tau distance can be used to count the pairwise disagreements of two rankings. Thus, the higher the Kendall tau distance, the more the rankings disagree.

A way to calculate Kendall tau distance is to count the number of pairs of items that are in different order in the two rankings. The number of pairs of items that are in different order in the two rankings is the Kendall tau distance.

For example, if we have two rankings:

- `Ranking A: 1, 2, 3, 4`
- `Ranking B: 3, 2, 1, 4`

The Kendall tau distance is 3, since there are 3 pairs of items that are in different order: (1, 2), (1, 3), (2, 3).

We will use the following notation for Kendall tau distance:

$$ \tau_{A, B} = 3 $$

The Kendall tau distance requires that the two rankings have the same items. Thus, our method will first compute the intersection of the two rankings, and then compute the Kendall tau distance.

Kendall tau distance calculation is implemented in the `disagreement.py/kendall_tau` function.

##### Kendall tau disagreement

Disagreement captures the differences in the item ratings between group members. It can be defined with a multitude of different methods. However, we have chosen to define strong disagreement to be when Kendall Tau values are very different from each other. Similarly, strong agreement is when the Kendall Tau values are very similar.

Now disagreement $d$ for movie ranking $R$ and users' personal movie suggestion rankings $M_u$ of user $u$ in the group $g$ is defined as follows:
<!-- Ei tarvita itsenäisarvoja, koska max on aina suurempi kuin min -->
$$ d_R = \max_{u\in g} \tau_{R, M_u} - \min_{u\in g} \tau_{R, M_u} $$

For example, for a group of movie recommendations and two users. Now for one movie ranking, the Kendall tau distance for one user is $0.8$ and for another user $0.2$. Now their disagreement would be $|0.8-0.2| = 0.6$.

Disagreement value calculation is implemented in the `disagreement.py/kendall_tau_disagreement` function.

#### **Propose a method that takes disagreements into account when computing suggestions for the group. Implement your method and explain why it is useful when producing group recommendations**

We have chosen to implement a modified version of a known algorithm, so let's first introduce the Kemeny-Young method. The logic is as follows:

1. Generate a permutation of the items (movies) in the group recommendations.
2. Calculate the Kendall tau distance between the permutation and the group members' rankings.
3. Sum the Kendall tau distances (calculated at step 2) for all group members.
4. Repeat steps 1-3 for all permutations.
5. Choose the permutation that minimizes the sum of Kendall tau distances.

Now we have chosen to use the disagreement defined above as the value to be minimized in the method. Thus the aggregation of top-10 movies recommended to the users in the group is performed following the steps:

1. Find the movies that are in all users' recommendations and find the common ones.
2. From all the movie permutations, find the one which minimizes disagreement defined above.
3. This is now the group movie recommendations, where the disagreement between users is the smallest.

Note that at step 1, we go through the users' recommendations in the order of:

1. The first movies in each users' recommendations.
2. The second movies in each users' recommendations.
3. etc. until we have found 10 movies that are in all users' recommendations.

Our proposed method is now able to take into account disagreement via the metric defined above. Due to how it is defined, our method minimizes the disparity between user opinions, ensuring that not only do the recommendations align with the members of the group but also conciders their disagreement with each other. 

In average aggregation the group recommendations may have movies which are suitable for some users but not for others. In least misery aggregation the recommendations may be movies that nobody hates but nobady really likes either. Our method however tries to minimize the disagreement between users, where the distance between their personal recommendations is minimized. This now means that the results should be both liked by the users but also where their opinions align with each other. 

The implementation for our proposed group recommendation aggregation method can be found in the `disagreement.py/modified_kemeny_young` function. The function is extremely slow, since it has to go through all the permutations of the movies.

#### **Use again the group of 3 users, and for this group, show the top-10 recommendations, i.e., the 10 movies with the highest prediction scores that your method suggests. Use the MovieLens 100K rating dataset**

```txt
Modified Kemeny-Young aggregation:
923
296
541
1198
1193
1952
1259
5902
5481
430
```

#### **Prepare also a short presentation (about 5 slides) to show how your method works in Assignment 2, Part (b)**

This presentation can be found in our repository `assignment2/asg2_presentation.pdf`.
