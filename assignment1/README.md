# Assignment 1: User-based Collaborative Filtering Recommendations


## Implementation Details and Assumptions
- Similarity measure calculations  
We perform calculations only for data where there are at least 3 movies both users have rated. Otherwise the similarity measure value is 0.
- For our results we have selected USER_ID = 233.
- We print all results to console output.
- User needs to provide path when calling the script. Usage:  
``` python assignment1.py -p/--path <path/to/ml-latest-small>```

## Results

### a) download and display rating data

```txt
Ratings downloaded, number of ratings: 100836
   userId  movieId  rating  timestamp
0       1        1     4.0  964982703
1       1        3     4.0  964981247
2       1        6     4.0  964982224
3       1       47     5.0  964983815
4       1       50     5.0  964982931
5       1       70     3.0  964982400
6       1      101     5.0  964980868
7       1      110     4.0  964982176
8       1      151     5.0  964984041
9       1      157     5.0  964984100
```

### b) User-based Collaborative Filtering Approach, pearson correlation between users

Pearson correlation has been implemented in the `pearson_corr` function. Similar users are calculated in the `get_similar_users` function.

### c) prediction function for movie scores

The prediction function is implemented in the `predict` function.

### d) select user, show 10 most similar users and 10 most relevant movies

```txt
Top-10 most similar users to user 233
157
9
120
473
97
568
349
90
604
278

Top-10 most relevant movies for user 233
923
1198
5481
5902
5952
3897
7361
785
3752
2
```

### e) design and implement adjusted cosine similarity

Various text books [1] and articles, as well as course material, have suggested cosine similarity as an option for computing the similarity of two users in collaborative filtering. 

An article by Fethi Fkih [2] compares different similarity measures for user-based collaborative filtering of the MovieLans dataset. The article demonstrates that cosine similarity while not performing quite as well as newly innovated and complex measures, works well for this application. Since it is also known to work well in various sources, we chose this as the baseline for our similarity.

Something interesting to note is that the cosine similarity does not concider user biases by normalizing the data. This is something handled in the Pearson correlation. Especially user ratings seem to be easily biased (a user may be prone to give 5s while anothe 1s, thus their ratings overall not being very useful). Due to this we decided to investigate an option to normalize the data and found the *adjusted cosine similarity*. 

The adjusted cosine similarity normalizes the data similarly as in Pearson correlation calculations which takies into account user bias. In addition, it addresses the sparsity problem of these often being missing ratings. We decided to implement both the "normal" cosine similarity function (for potential future use) as well as the adjusted version.

1. Ricci, Francesco., Lior. Rokach, and Bracha. Shapira, eds. Recommender Systems Handbook. 2nd ed. 2015. New York, NY: Springer US, 2015. Web.

2. Fkih, Fethi. “Similarity Measures for Collaborative Filtering-Based Recommender Systems: Review and Experimental Comparison.” Journal of King Saud University. Computer and information sciences 34.9 (2022): 7645–7669. Web.


Both adjusted and normal cosine similarity has been implemented in the `cosine_sim` function. 

```txt
Top-10 most similar users to user 233
157
9
120
473
97
568
349
90
604
278

Top-10 most relevant movies for user 233
923
1198
5481
5902
5952
3897
7361
785
3752
2
```
