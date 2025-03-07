from src.recommendation_system.recommendation_flow.candidate_generators.RandomGenerator import (
    RandomGenerator,
)
from src.recommendation_system.recommendation_flow.controllers.AbstractController import (
    AbstractController,
)
from src.recommendation_system.recommendation_flow.filtering.RandomFilter import (
    RandomFilter,
)
from src.recommendation_system.recommendation_flow.model_prediction.RandomModel import (
    RandomModel,
)
from src.recommendation_system.recommendation_flow.ranking.RandomRanker import (
    RandomRanker,
)
from src.api.metrics.models import TeamName

class RandomController(AbstractController):
    def get_content_ids(self, user_id, limit, offset, seed, starting_point):
        if seed <= 1:  # MySql seeds should be [0, # of rows] not [0, 1]
            seed *= 1000000
        candidates_limit = (
            limit * 10 * 10
        )  # 10% gets filtered out and take top 10% of rank
        candidates, scores = RandomGenerator().get_content_ids(
            TeamName.Random,
            user_id, candidates_limit, offset, seed, starting_point
        )
        filtered_candidates = RandomFilter().filter_ids(
            TeamName.Random, user_id, candidates, seed, starting_point, amount=0.1
        )
        predictions = RandomModel().predict_probabilities(
            TeamName.Random,
            filtered_candidates,
            user_id,
            seed=seed,
            scores={
                content_id: {"score": score}
                for content_id, score in zip(candidates, scores)
            }
            if scores is not None
            else {},
        )
        rank = RandomRanker().rank_ids(TeamName.Random, user_id, filtered_candidates, limit, predictions, seed, starting_point)
        return rank
