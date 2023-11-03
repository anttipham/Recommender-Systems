# Assignment 1: User-based Collaborative Filtering Recommendations

## Assumptions

## Implementation Details

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
