"""
DATA.ML.360 Recommender Systems - Assignment 3
Main file for the assignment.

Antti Pham, Sophie Tötterström
"""

import disagreement as disag
import pandas as pd

import assignment1 as asg1
import assignment2 as asg2

N = 10
GROUP = [233, 9, 242]
# GROUP = [233, 423, 242]
SIMILARITY_TYPE = "pearson"
ITERATIONS = 3


def calc_satisfaction(group_recs: list[int], user_recs: list[int]) -> float:
    """
    Calculates satisfaction score for one user.

    Satisfaction is defined from the Kendall tau distance between
    the group recommendations and the user's personal recommendations.
    But this value is normalized and adjusted such that the satisfaction score
    of 1 means that the recommendations are identical and 0 means that the
    recommendations are completely different.

    This is similar to the satisfaction score in the course
    material (lecture 7, slide 12) where GroupListSatisfaction is divided by
    a normalizing value (UserListSatisfaction).

    Args:
        group_recs (list[int]): Movie recommendations for the group in the order
                                of best to worst.
        user_recs (list[int]): Personal movie recommendations for one user in
                               the order of best to worst.

    Returns:
        float: Satisfaction score.
    """
    satisfation = 1 - disag.kendall_tau_normalized(group_recs, user_recs)
    return satisfation


def next_alpha(satisfactions: list[float]) -> float:
    """
    Calculate next alpha from the satisfaction scores of the previous iteration.

    Alpha is in the range of [0, 1].

    Args:
        satisfactions (list[float]): Satisfaction scores of the previous
                                           iteration for each user.

    Returns:
        float: Next alpha score.
    """
    return max(satisfactions) - min(satisfactions)


def weighted_combination(
    least_misery: dict[int, float],
    average: dict[int, float],
    alpha: float,
) -> list[tuple[int, float]]:
    """
    Calculate the weighted combination of the group aggregated scores of least
    misery and average methods, weighted appropriately with the alpha value.

    This is done following the sequential hybrid aggregation model presented in
    course material (lecture 7, slide 17).

    Args:
        least_misery (dict[int, float]): the movie, ratings pairs for the group,
                                         aggregated with the least misery method.
        average (dict[int, float]): the movie, ratings pairs for the group,
                                    aggregated with the average method.
        alpha (float): Alpha value of this iteration.

    Returns:
        list[tuple[int, float]]: The group recommendations in descending order.
    """

    scores: dict[int, float] = {}
    for movie_id, avg_rating in average.items():
        least_rating = least_misery[movie_id]
        scores[movie_id] = (1 - alpha) * avg_rating + alpha * least_rating
    return asg2.get_sorted_group_recs(scores)


def get_movie_ratings_for_users(
    user_movie_df: pd.DataFrame,
) -> dict[int, list[tuple[int, float]]]:
    """
    Gets user specific recommendations for all group members.

    Args:
        user_movie_df (pd.DataFrame): ratings dataset

    Returns:
        dict[int, list[tuple[int, float]]]: user_id, recommendation pairs
    """

    recs: dict[int, list[tuple[int, float]]] = {}
    for user in GROUP:
        recs[user] = asg1.get_top_movies(user_movie_df, user, SIMILARITY_TYPE)
    return recs


def main():
    # Read data
    user_movie_df = asg1.read_movielens(ratings_file_path=asg1.parse_args())

    # Get recommendations for all group members and aggregate
    recs = get_movie_ratings_for_users(user_movie_df)
    avg_group_recs = asg2.average_aggregate(user_movie_df, recs, return_only_pred=True)
    least_misery_group_recs = asg2.least_misery_aggregate(
        user_movie_df, recs, return_only_pred=True
    )

    # set alpha for first iteration to 0 so only consider average aggregation
    alphas = [0.0]
    for iteration in range(ITERATIONS):
        # Hybrid aggregation
        hybrid_group_recs = weighted_combination(
            avg_group_recs, least_misery_group_recs, alpha=alphas[iteration]
        )
        hybrid_recs = asg2.nth_elements(hybrid_group_recs, 1)

        # Display results
        print(f"\n## Iteration {iteration+1}, alpha={alphas[iteration]:.2} ##")
        print(f"Top-{N} Hybrid Recommendations for group {GROUP}")
        for movie, rating in hybrid_group_recs[:N]:
            print(f"Movie number: {movie},\tPredicted rating: {rating:.3}")

        # Finally update alpha for future iterations
        satisfactions = [
            calc_satisfaction(hybrid_recs[:N], asg2.nth_elements(recs[user], 1))
            for user in GROUP
        ]
        alphas.append(next_alpha(satisfactions))
        # print()
        # print(*satisfactions, sep="\n")


if __name__ == "__main__":
    main()
